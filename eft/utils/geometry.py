# Copyright (c) Facebook, Inc. and its affiliates.

#Modified from https://github.com/nkolot/SPIN/blob/master/LICENSE

import torch
from torch.nn import functional as F
import numpy as np

"""
Useful geometric operations, e.g. Perspective projection and a differentiable Rodrigues formula
Parts of the code are taken from https://github.com/MandyMo/pytorch_HMR
"""
def batch_rodrigues(theta):
    """Convert axis-angle representation to rotation matrix.
    Args:
        theta: size = [B, 3]
    Returns:
        Rotation matrix corresponding to the quaternion -- size = [B, 3, 3]
    """
    l1norm = torch.norm(theta + 1e-8, p = 2, dim = 1)
    angle = torch.unsqueeze(l1norm, -1)
    normalized = torch.div(theta, angle)
    angle = angle * 0.5
    v_cos = torch.cos(angle)
    v_sin = torch.sin(angle)
    quat = torch.cat([v_cos, v_sin * normalized], dim = 1)
    return quat_to_rotmat(quat)

def quat_to_rotmat(quat):
    """Convert quaternion coefficients to rotation matrix.
    Args:
        quat: size = [B, 4] 4 <===>(w, x, y, z)
    Returns:
        Rotation matrix corresponding to the quaternion -- size = [B, 3, 3]
    """ 
    norm_quat = quat
    norm_quat = norm_quat/norm_quat.norm(p=2, dim=1, keepdim=True)
    w, x, y, z = norm_quat[:,0], norm_quat[:,1], norm_quat[:,2], norm_quat[:,3]

    B = quat.size(0)

    w2, x2, y2, z2 = w.pow(2), x.pow(2), y.pow(2), z.pow(2)
    wx, wy, wz = w*x, w*y, w*z
    xy, xz, yz = x*y, x*z, y*z

    rotMat = torch.stack([w2 + x2 - y2 - z2, 2*xy - 2*wz, 2*wy + 2*xz,
                          2*wz + 2*xy, w2 - x2 + y2 - z2, 2*yz - 2*wx,
                          2*xz - 2*wy, 2*wx + 2*yz, w2 - x2 - y2 + z2], dim=1).view(B, 3, 3)
    return rotMat    






def cross_product(u, v):
    batch = u.shape[0]
    i = u[:, 1] * v[:, 2] - u[:, 2] * v[:, 1]
    j = u[:, 2] * v[:, 0] - u[:, 0] * v[:, 2]
    k = u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0]
        
    out = torch.cat((i.view(batch, 1), j.view(batch, 1), k.view(batch, 1)), 1)
        
    return out

def normalize_vector(v):
    batch = v.shape[0]
    v_mag = torch.sqrt(v.pow(2).sum(1))  # batch
    v_mag = torch.max(v_mag, v.new([1e-8]))
    v_mag = v_mag.view(batch, 1).expand(batch, v.shape[1])
    v = v/v_mag
    return v

#Code from
def rot6d_to_rotmat(x):
    """Convert 6D rotation representation to 3x3 rotation matrix.
    Based on Zhou et al., "On the Continuity of Rotation Representations in Neural Networks", CVPR 2019
    Input:
        (B,6) Batch of 6-D rotation representations
    Output:
        (B,3,3) Batch of corresponding rotation matrices
    """
    x = x.view(-1,3,2)
    a1 = x[:, :, 0]
    a2 = x[:, :, 1]
    b1 = F.normalize(a1)
    b2 = F.normalize(a2 - torch.einsum('bi,bi->b', b1, a2).unsqueeze(-1) * b1)
    b3 = torch.cross(b1, b2)
    return torch.stack((b1, b2, b3), dim=-1)


# #https://github.com/hassony2/manopth/blob/master/manopth/rot6d.py
# def compute_rotation_matrix_from_ortho6d(poses):
#     """
#     Code from
#     https://github.com/papagina/RotationContinuity
#     On the Continuity of Rotation Representations in Neural Networks
#     Zhou et al. CVPR19
#     https://zhouyisjtu.github.io/project_rotation/rotation.html
#     """
#     x_raw = poses[:, 0:3]  # batch*3
#     y_raw = poses[:, 3:6]  # batch*3
        
#     x = normalize_vector(x_raw)  # batch*3
#     z = cross_product(x, y_raw)  # batch*3
#     z = normalize_vector(z)  # batch*3
#     y = cross_product(z, x)  # batch*3
        
#     x = x.view(-1, 3, 1)
#     y = y.view(-1, 3, 1)
#     z = z.view(-1, 3, 1)
#     matrix = torch.cat((x, y, z), 2)  # batch*3*3
#     return matrix

# def robust_compute_rotation_matrix_from_ortho6d(poses):
#     """
#     Instead of making 2nd vector orthogonal to first
#     create a base that takes into account the two predicted
#     directions equally
#     """
#     x_raw = poses[:, 0:3]  # batch*3
#     y_raw = poses[:, 3:6]  # batch*3

#     x = normalize_vector(x_raw)  # batch*3
#     y = normalize_vector(y_raw)  # batch*3
#     middle = normalize_vector(x + y)
#     orthmid = normalize_vector(x - y)
#     x = normalize_vector(middle + orthmid)
#     y = normalize_vector(middle - orthmid)
#     # Their scalar product should be small !
#     # assert torch.einsum("ij,ij->i", [x, y]).abs().max() < 0.00001
#     z = normalize_vector(cross_product(x, y))

#     x = x.view(-1, 3, 1)
#     y = y.view(-1, 3, 1)
#     z = z.view(-1, 3, 1)
#     matrix = torch.cat((x, y, z), 2)  # batch*3*3
#     # Check for reflection in matrix ! If found, flip last vector TODO
#     assert (torch.stack([torch.det(mat) for mat in matrix ])< 0).sum() == 0
#     return matrix


     
def perspective_projection(points, rotation, translation,
                           focal_length, camera_center):
    """
    This function computes the perspective projection of a set of points.
    Input:
        points (bs, N, 3): 3D points
        rotation (bs, 3, 3): Camera rotation
        translation (bs, 3): Camera translation
        focal_length (bs,) or scalar: Focal length
        camera_center (bs, 2): Camera center
    """
    batch_size = points.shape[0]
    K = torch.zeros([batch_size, 3, 3], device=points.device)
    K[:,0,0] = focal_length
    K[:,1,1] = focal_length
    K[:,2,2] = 1.
    K[:,:-1, -1] = camera_center

    # Transform points
    points = torch.einsum('bij,bkj->bki', rotation, points)
    points = points + translation.unsqueeze(1)

    # Apply perspective distortion
    projected_points = points / points[:,:,-1].unsqueeze(-1)

    # Apply camera intrinsics
    projected_points = torch.einsum('bij,bkj->bki', K, projected_points)

    return projected_points[:, :, :-1]


def estimate_translation_np(S, joints_2d, joints_conf, focal_length=5000, img_size=224):
    """Find camera translation that brings 3D joints S closest to 2D the corresponding joints_2d.
    Input:
        S: (25, 3) 3D joint locations
        joints: (25, 3) 2D joint locations and confidence
    Returns:
        (3,) camera translation vector
    """

    num_joints = S.shape[0]
    # focal length
    f = np.array([focal_length,focal_length])
    # optical center
    center = np.array([img_size/2., img_size/2.])

    # transformations
    Z = np.reshape(np.tile(S[:,2],(2,1)).T,-1)
    XY = np.reshape(S[:,0:2],-1)
    O = np.tile(center,num_joints)
    F = np.tile(f,num_joints)
    weight2 = np.reshape(np.tile(np.sqrt(joints_conf),(2,1)).T,-1)

    # least squares
    Q = np.array([F*np.tile(np.array([1,0]),num_joints), F*np.tile(np.array([0,1]),num_joints), O-np.reshape(joints_2d,-1)]).T
    c = (np.reshape(joints_2d,-1)-O)*Z - F*XY

    # weighted least squares
    W = np.diagflat(weight2)
    Q = np.dot(W,Q)
    c = np.dot(W,c)

    # square matrix
    A = np.dot(Q.T,Q)
    b = np.dot(Q.T,c)

    # solution
    trans = np.linalg.solve(A, b)

    return trans


def estimate_translation(S, joints_2d, focal_length=5000., img_size=224.):
    """Find camera translation that brings 3D joints S closest to 2D the corresponding joints_2d.
    Input:
        S: (B, 49, 3) 3D joint locations
        joints: (B, 49, 3) 2D joint locations and confidence
    Returns:
        (B, 3) camera translation vectors
    """

    device = S.device
    # Use only joints 25:49 (GT joints)
    S = S[:, 25:, :].cpu().numpy()
    joints_2d = joints_2d[:, 25:, :].cpu().numpy()
    joints_conf = joints_2d[:, :, -1]
    joints_2d = joints_2d[:, :, :-1]
    trans = np.zeros((S.shape[0], 3), dtype=np.float32)
    # Find the translation for each example in the batch
    for i in range(S.shape[0]):
        S_i = S[i]
        joints_i = joints_2d[i]
        conf_i = joints_conf[i]
        trans[i] = estimate_translation_np(S_i, joints_i, conf_i, focal_length=focal_length, img_size=img_size)
    return torch.from_numpy(trans).to(device)




def weakProjection_gpu(skel3D, scale, trans2D ):
    # if len(skel3D.shape)==1:
    #     skel3D = np.reshape(skel3D, (-1,3))

    skel3D = skel3D.view((skel3D.shape[0],-1,3))
    trans2D = trans2D.view((trans2D.shape[0],1,2))
    scale = scale.view((scale.shape[0],1,1))
    skel3D_proj = scale* skel3D[:,:,:2] + trans2D

    return skel3D_proj#skel3D_proj.view((skel3D.shape[0],-1))       #(N, 19*2) o


#(N,57) (N,) (N,2)
def weakProjection_batch(skel3D, scale, trans2D ):
    # if len(skel3D.shape)==1:
    #     skel3D = np.reshape(skel3D, (-1,3))

    skel3D = np.reshape(skel3D, (skel3D.shape[0],-1,3))
    trans2D = np.reshape( trans2D, (trans2D.shape[0],1,2))
    scale = np.reshape(scale, (scale.shape[0],1,1))
    skel3D_proj = scale* skel3D[:,:,:2] + trans2D

    return skel3D_proj#skel3D_proj.view((skel3D.shape[0],-1))       #(N, 19*2) o


#(57) (1) (2)
def weakProjection(skel3D, scale, trans2D ):

    skel3D_proj = scale* skel3D[:,:2] + trans2D

    return skel3D_proj#skel3D_proj.view((skel3D.shape[0],-1))       #(N, 19*2) o
