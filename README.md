# [Exemplar Fine-Tuning for 3D Human Pose Fitting Towards In-the-Wild 3D Human Pose Estimation](https://arxiv.org/abs/2004.03686)

This repository contains pseudo-GT 3D pose data data produced by [Exemplar Fine-Tuning (EFT)](https://arxiv.org/abs/2004.03686) method. The 3D pose data is in the form of [SMPL](https://smpl.is.tue.mpg.de/) parameters. 

![Teaser Image](docs/example1.jpg)
![Teaser Image](docs/example2.jpg)

## Requirements
- python3
- numpy
- opencv-python
- PyTorch (1.4.0 or 1.5.0 but lower version would be still OK)
- torchvision
- PyOpenGL
- smplx
- [chumpy](https://github.com/mattloper/chumpy) (required to load SMPL model)
- scipy
- tqdm

## Download EFT Fitting Results

This repository only provides corresponding SMPL parameters for public 2D keypoint datasets (such as [COCO](https://cocodataset.org/), [MPII](http://human-pose.mpi-inf.mpg.de/)). You need to download images from the original dataset website.

## Download EFT Fitting data (json formats)
Run the following script
```
sh scripts/download_eft.sh 
```
   - The EFT data will be saved in ./eft_fit/(DB_name).json. Each json file contains a version EFT fitting for a public dataset. 
   - See [Data Format](docs/README_dataformat.md) for details
   - Currently available EFT fitting outputs (cvpr submit version):
      - COCO2014-All-ver01.json: COCO 2014 training set. 79051 samples, selecting the samples 6 keypoints or more keypoints are annotated.
      - COCO2014-Part-ver01.json: COCO 2014 training set (a subset). 28344 samples, selecting the sample that all 12 limb keypoints are annotated.
      - MPII_ver01.json : MPII Keypoint Dataset
      - LSPet_ver01.json : LSPet Dataset
      - Panoptic: TBA

### Download Other Required Data
- SMPL Model (Neutral model: basicModel_neutral_lbs_10_207_0_v1.0.0.pkl):
    - Download in the original [website](http://smplify.is.tue.mpg.de/login). You need to register to download the SMPL data.
    - Put the file in: ./extradata/smpl/basicModel_neutral_lbs_10_207_0_v1.0.0.pkl

- Densepose (optional, for Densepose rendering): 
  - Run the following script
  ```
      sh scriptsdownload_dp_uv.sh    
  ```
  - Files are saved in ./extradata/densepose_uv_data/
  
## Download Images from Original Public DB website
 - [COCO](https://cocodataset.org/#home): [2014 Training set](http://images.cocodataset.org/zips/train2014.zip)
 - [MPII](http://human-pose.mpi-inf.mpg.de/): [Download Link](https://datasets.d2.mpi-inf.mpg.de/andriluka14cvpr/mpii_human_pose_v1.tar.gz)
 - [LSPet](https://sam.johnson.io/research/lspet.html): [Download Link](http://datasets.d2.mpi-inf.mpg.de/hr-lspet/hr-lspet.zip)

## Visualize EFT Fitting Results
- See [GETTING_STARTED](docs/GETTING_STARTED.md)

## Citation
```
@article{joo2020eft,
  title={Exemplar Fine-Tuning for 3D Human Pose Fitting Towards In-the-Wild 3D Human Pose Estimation},
  author={Joo, Hanbyul and Neverova, Natalia and Vedaldi, Andrea},
  journal={arXiv preprint arXiv:2004.03686},
  year={2020}
}
```

## License
[CC-BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/legalcode). 
See the [LICENSE](LICENSE) file. 


