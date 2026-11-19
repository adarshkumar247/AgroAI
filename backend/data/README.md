# AgroAI Dual-Source 11-Class Balanced Benchmark

This dataset is configured specifically for the AgroAI smart crop disease detection pipeline.

## Dataset Specifications
- **Classes**: 11
- **Images per class**: 150
- **Total Images**: 1650
- **Sampling Strategy**: Uniformly balanced 1:1 class ratio (150 images per class)
- **Train / Validation Split**: 80% Train (120 per class) / 20% Validation (30 per class)

## Dataset Sources & Attribution

### 1. PlantVillage Dataset (10 Classes)
- **Source**: Penn State University / EPFL
- **Citation**: Hughes, D. P., & Salathé, M. (2015). *An open access repository of images on plant health to enable the development of mobile disease diagnostics.* arXiv preprint arXiv:1511.08060.
- **License**: Creative Commons Zero 1.0 Universal (CC0 1.0) / Public Domain
- **Included Classes**:
  1. `Tomato___Early_blight`
  2. `Tomato___Late_blight`
  3. `Tomato___Target_Spot`
  4. `Tomato___healthy`
  5. `Potato___Early_blight`
  6. `Potato___Late_blight`
  7. `Potato___healthy`
  8. `Corn___Common_rust_`
  9. `Corn___Northern_Leaf_Blight`
  10. `Corn___healthy`

### 2. Rice Leaf Disease Dataset (1 Class)
- **Source**: Mendeley Data / Prajapati et al. / Rahman et al.
- **Citation**: Rahman, C. R., et al. (2020). *RiceLeafBD: A comprehensive dataset of rice leaf diseases for deep learning.* Mendeley Data, DOI: 10.17632/kx9rx8p2mz.1.
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Included Class**:
  11. `Rice___Brown_spot` (*Bipolaris oryzae*)
