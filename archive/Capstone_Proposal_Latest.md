## Accessible Distance Learning: Reducing Network Demand through Client-Side Super-Resolution and Frame Generation 

Mithila Mostofa Tonni, Md. Sadik Shahriar, Md Fokrul Akon, and Syed Zubayear Bin Khaled Department of Computer Science and Engineering, East West University 

_**Abstract**_ **—Educational video conferencing over WebRTC suffers from severe quality degradation in low-bandwidth environments, rendering whiteboard-based instruction illegible. This research proposes a client-side, browser-native enhancement pipeline to mitigate these artifacts without increasing network demand. The solution utilizes a dual-stage neural framework consisting of video frame interpolation (VFI) and video superresolution (VSR). The pipeline is initialized with a RIFE backbone fine-tuned on a purpose-built whiteboard lecture dataset and an ESPCN-INT8 model trained from scratch using a composite wavelet and LPIPS loss function. Deployment is achieved via a Chrome browser extension that leverages the Insertable Streams API and the TensorFlow.js WebGPU backend for realtime inference on consumer-grade integrated graphics. This study contributes the first whiteboard-specific VSR benchmark dataset, optimized neural checkpoints for handwriting preservation, and an empirical evaluation of the latency and energy trade-offs of edge-native video enhancement. Preliminary results target a sub-200 ms end-to-end processing latency to maintain real-time interactivity.** 

## I. INTRODUCTION 

Distance learning serves as a primary mode of instruction for millions of students globally, yet the underlying network infrastructure often remains inadequate. In bandwidthconstrained environments, such as rural connections, congested campus Wi-Fi, or mobile data plans in developing regions, WebRTC-based video conferencing systems respond by aggressively down-sampling the media stream. This results in resolutions dropping from 1080p to 360p and frame rates falling from 30 fps to 10 fps. While these degradations are tolerable for general conversation, they render whiteboardbased lectures illegible. The underlying scenario assumes a bidirectional educational video call where instructor-led whiteboard annotations must be preserved despite severe networkinduced artifacts. This research assumes that the student’s local hardware possesses a modern integrated graphics processor (iGPU) capable of hardware-accelerated inference. 

using convolutional or transformer-based neural networks to reconstruct high-frequency details from low-resolution inputs. Frame Interpolation focuses on synthesizing intermediate frames between existing ones to restore temporal smoothness. Traditionally, these tasks were handled separately and required high-end discrete GPUs. However, recent advances in model quantization and browser-native APIs like WebGPU now allow for the execution of these models directly on client-side hardware within the browser environment. 

## III. PROBLEM STATEMENT 

The primary challenge in interactive distance learning is the quality collapse of video streams under network congestion, which specifically obscures high-frequency geometric content like handwriting and mathematical notation. This problem is significant because it creates an educational barrier for students in low-bandwidth regions who cannot follow visual derivations. Current state-of-the-art solutions typically rely on cloud-based AI restoration, but this approach is infeasible for real-time calls due to the added round-trip latency that violates the 200 ms interactivity threshold. Furthermore, existing local enhancement models are often designed for general cinematic content and tend to over-smooth educational text, leading to illegible characters. Small changes to these state-of-theart approaches are insufficient because they do not address the fundamental tension between the high compute cost of a cascaded VFI-VSR pipeline and the strict latency and thermal constraints of consumer integrated graphics. 

## IV. AIM 

The aim of this research is to design and evaluate a clientside, dual-stage AI video enhancement pipeline that restores motion smoothness and spatial resolution for educational WebRTC streams on consumer-grade integrated graphics. 

## V. OBJECTIVES 

## II. BACKGROUND 

Understanding the proposed solution requires foundational knowledge of three technical domains: WebRTC transport, Video Super-Resolution (VSR), and Video Frame Interpolation (VFI). WebRTC is the industry standard for real-time communication, utilizing adaptive bitrate algorithms that prioritize low latency over visual fidelity by dropping frames and reducing spatial resolution. Super-Resolution involves 

The research aims to achieve the following three objectives. First, the study will develop a lightweight dual-stage neural pipeline optimized for the preservation of high-frequency geometric structures in whiteboard handwriting. Second, the work will apply post-training INT8 quantization via PyTorch’s torch.ao.quantization API and deploy the resulting models through the TensorFlow.js WebGPU backend to achieve sub200 ms end-to-end processing latency on consumer integrated 

graphics. Third, the project will analyze the performance tradeoffs between transmission bandwidth reduction and the local power consumption costs on edge devices. 

## VI. CONTRIBUTIONS 

This research makes three original contributions that do not currently exist in the literature. First, the work provides a purpose-built whiteboard lecture dataset of approximately 8 hours with matched low-resolution and high-resolution pairs degraded under documented WebRTC-realistic FFmpeg parameters, a resource that no existing video super-resolution benchmark provides. A systematic review of six publicly available VSR benchmarks, including REDS, Vimeo-90K, Vid4, UDM10, RealVSR, and DAVIS, confirmed that none contain whiteboard lecture content degraded under documented WebRTC codec parameters. Second, the project introduces a dual-stage video frame interpolation and super-resolution pipeline fine-tuned specifically on educational handwriting and mathematical notation using a composite wavelet and LPIPS loss, addressing a domain that existing pipelines optimized for cinematic content do not adequately serve. 

The third contribution is a fully functional browser extension implementing this pipeline via the Insertable Streams API on consumer integrated graphics. This implementation produces the first end-to-end latency and energy measurement of client-side neural video enhancement inside a live WebRTC session. By demonstrating the feasibility of browser-native enhancement, the work establishes a new technical framework for reducing network demand without sacrificing the legibility of educational materials. 

## VII. RELATED WORKS 

Educational video conferencing over WebRTC is acutely sensitive to network degradation. Fouladi et al. demonstrated that even state-of-the-art codec–transport co-designs cannot prevent severe quality collapse when available bandwidth fluctuates [1]. Consequently, any viable restoration pipeline must execute locally on the receiver’s own edge hardware. Recent hardware advances confirm that client-side neural inference is feasible. Liu’s ANVIL system achieves 12.8 ms inference latency for frame interpolation on mobile NPUs [2], while Fazel and Bentaleb’s VSR-Bench demonstrates that WebGPUaccelerated super-resolution models sustain sub-30 ms latency directly inside a WebRTC receiver [3]. 

Visual fidelity in educational streams presents a challenge that generic AI enhancement overlooks: the preservation of hard-edged, high-frequency geometric content. Kong et al. address this in WaveletVFI by performing frame interpolation in the wavelet domain, enabling a dedicated frequency-domain reconstruction loss that enforces structure awareness [4]. Similarly, IFRNet introduces a feature-space geometry consistency loss to prevent topology-breaking artifacts [5]. Zhang et al. established that Learned Perceptual Image Patch Similarity (LPIPS) is a superior metric for quantifying these structural ambiguities compared to traditional SSIM [6]. Finally, Geng et al. highlight that treating space-time enhancement as a simple 

cascade often duplicates feature extraction, identifying a need for efficient unified pipelines [7]. 

The transition from cloud-based restoration to edge-native inference requires architectural paradigms that balance temporal consistency with limited computational budgets. Sajjadi et al. proposed the Frame-Recurrent Video Super-Resolution (FRVSR) framework, which leverages previously inferred high-resolution estimates to super-resolve subsequent frames [8]. Their benchmarks show that a 3-block architecture achieves Full HD upscaling in 74 ms, whereas a more complex 10-block version requires 191 ms. Yang et al. introduced the Spatial-Temporal Recurrent Residual Network (STR-ResNet), which unifies CNN and RNN architectures to model interframe correlations without requiring explicit optical flow [9]. For handheld educational recordings, Fang et al. developed a parallel-fusion module that adaptively fuses deblurring and SR features [10]. Huang et al. utilized a bidirectional recurrent convolutional network (BRCN) that captures repetitive patterns of transformation as abstract hidden layers, demonstrating processing speeds of 0.48 sec/frame on dedicated hardware [11]. Furthermore, Fuoli et al. achieved a 70 _×_ speed-up over previous state-of-the-art methods with Recurrent Latent Space Propagation (RLSP), generating 50 FPS Full HD video at a 19 ms inference latency [12]. 

Efficiency is further improved through knowledge distillation and hardware-aware optimization. Wen et al. proposed the CGSR framework, which employs dynamic weight pruning to reduce latency by an average of 30% and parameter counts by up to 77%, specifically reducing inference times from 11 ms to 8 ms for 2 _×_ upscaling and 13 ms to 10 ms for 3 _×_ upscaling [13]. Recognizing the gap between synthetic and practical performance, Yang et al. introduced the RealVSR dataset captured via mobile multi-camera systems [14]. Deployment optimization is addressed by Lee et al. through MobiSR, whose heterogeneous scheduler achieves speedups of 2.13 _×_ to 4.79 _×_ compared to a 1.4 s baseline for mobile 4 _×_ upscaling [15]. Similarly, Hirose et al. validated the feasibility of edge AI by demonstrating that INT8 precision models can achieve benchmarks of 51.95 FPS on targeted hardware [16]. 

Finally, system-level constraints and energy efficiency are critical for battery-powered deployment. Burhanuddin noted that energy-efficient techniques like power gating can save up to 60% of energy and 40% of power in edge devices [17]. To manage real-time video analytics, Tan et al. proposed the FastVA framework, which offloads computation based on a strict 200 ms time constraint, noting that offloading becomes more energy-efficient than local processing when bandwidth exceeds 40 Mbps [18]. Further optimization for streaming is found in Kwon et al., whose CILVSR network achieves a 40 ms inference time by utilizing intrinsic compression data [19]. Rafiei et al. introduced a scalable architecture defining the Real-Time Viability Condition as _τ <_ 1 _._ 0, where optimal segment durations for stable playback are 3 seconds for enterprise hardware and 8 seconds for commodity tiers [20]. These existing works establish a foundation for low-latency enhancement, as summarized in Table I, yet they leave an 

unresolved gap regarding unified pipelines for whiteboardheavy educational content, leading to the research questions defined below. 

TABLE I 

COMPARATIVE PERFORMANCE BENCHMARK OF LIGHTWEIGHT VSR MODELS 

|**Model**|**Architecture**|**PSNR**|**SSIM**|**Latency**|**Source**|
|---|---|---|---|---|---|
|FRVSR 3-64|Frame-Recurrent|26.25 dB|0.803|74 ms (FHD)|[8]|
|RLSP 7-64|Recurrent Latent|26.65 dB|—|19 ms (FHD)|[12]|
|CILVSR|Compression-Inf.|—|0.630|40 ms|[19]|
|BRCN|Bidirectional Rec.|28.20 dB|0.633|0.48 sec/fr.|[11]|
|ESPCN (INT8)|Sub-Pixel Conv.|30.56 dB*|—|51.95 FPS|[16]|



*Note: ESPCN results reported on DIV2K with calibration. 

## VIII. RESEARCH QUESTIONS 

The central research question of this study is: can a clientside AI video enhancement pipeline successfully restore educational video quality from highly degraded network streams within the real-time latency constraints of interactive WebRTC communication on consumer-grade hardware? This inquiry is further decomposed into three specific sub-questions: 

- 1) **RQ1:** What is the impact of a dual-stage pipeline on the preservation of high-frequency geometric structures in whiteboard text? 

- 2) **RQ2:** To what extent can model quantization and WebGPU acceleration mitigate the latency overhead on integrated graphics hardware? 

- 3) **RQ3:** How does the local power consumption of the AI pipeline scale relative to the bandwidth savings achieved by low-bitrate transmission? 

## IX. PLANNED METHODOLOGY 

The research methodology follows a three-phase execution plan spanning ten weeks. Each phase has clearly defined inputs, outputs, and success criteria, and the phases are designed to overlap slightly so that implementation can begin before dataset construction is fully complete. The logical flow of the system is illustrated in the architectural framework in Figure 1. 

The first phase involves dataset construction (Weeks 1 to 3). The absence of a publicly available whiteboard lecture dataset degraded to WebRTC-realistic conditions necessitates a purpose-built corpus. Approximately 8 hours of whiteboard lecture footage will be recorded at 1080p/30 fps using a fixed-position webcam in a controlled indoor setting. Content will span four subject areas, including mathematics, physics, discrete structures, and Bengali script, to ensure coverage of diverse stroke geometries and character shapes relevant to the educational context. Each session will run 20 to 30 minutes and will be conducted by team members acting as instructors. Recording will use OBS Studio with x264 lossless encoding to preserve ground-truth pixel fidelity before any degradation is applied. The 1080p source footage will then be programmatically downsampled to 360p/10 fps using FFmpeg with the H.264 codec at a constrained bitrate of 150 to 300 kbps, replicating the behavior of WebRTC’s Google Congestion Control 

Fig. 1. Proposed dual-stage client-side enhancement framework, illustrating the integration of temporal frame interpolation and spatial super-resolution stages between the WebRTC receiver and the local display compositor. 

algorithm under low-bandwidth conditions. The specific FFmpeg parameters, including CRF value, keyframe interval, and B-frame count, will be fixed at the outset and documented to ensure full reproducibility. This process yields matched low-resolution and high-resolution frame pairs suitable for supervised training. The corpus will be divided into 70% training, 15% validation, and 15% test subsets, stratified by content type to prevent domain leakage. Ground-truth frames will be stored as lossless PNG sequences, and degraded frames will be stored as decoded JPEG sequences matching typical WebRTC decoder output. 

To document inter-session variability, each recording session will log the contributing team member, lighting conditions, and marker type used. These metadata fields will be included in the dataset manifest so that downstream researchers can stratify or control for handwriting style during evaluation. 

The second phase encompasses pipeline implementation (Weeks 3 to 8). The pipeline consists of two sequential neural stages, video frame interpolation followed by video super-resolution, implemented in Python using PyTorch for training and converted to ONNX for browser deployment. These two stages are developed in parallel by separate subteams and integrated in Week 7. The interpolation backbone will be initialized from the publicly available RIFE v4.6 checkpoint, which is selected for its demonstrated sub-20 ms latency profile on consumer hardware. The model will be finetuned on the whiteboard training split for 30 epochs using a composite loss that combines a Charbonnier term, which reduces sensitivity to outlier motion vectors around chalk strokes, with a wavelet loss applied on the Haar decomposition of predicted and ground-truth frames to penalize highfrequency structural errors. This wavelet component is adapted from WaveletVFI. The learning rate will be set to 1 _×_ 10 _[−]_[4] with cosine annealing. The target output of this stage is one synthesized intermediate frame per decoded pair, effectively converting a 10 fps stream to 20 fps. Fine-tuning will run 

on a single NVIDIA GPU available through university lab access, with Google Colab Pro serving as a fallback, and total training time is estimated at 18 to 24 hours. The superresolution model will be a compact variant of ESPCN with three residual convolutional blocks and a sub-pixel shuffle layer for 3 _×_ upscaling from 360p to 1080p. This architecture is chosen deliberately over heavier transformer-based models because ESPCN in INT8 precision is the only architecture in the surveyed literature confirmed to sustain above 50 frames per second on integrated GPU hardware. The model will be trained from scratch on the whiteboard dataset using a three-component composite loss combining pixel-wise _L_ 1 loss, LPIPS perceptual loss using a VGG backbone, and a wavelet loss term. Given that the training corpus is approximately 8 hours of footage, overfitting is a primary risk. This will be mitigated through early stopping with a patience of 5 validation epochs, dropout (p=0.1) after each residual block, and horizontal flip augmentation applied stochastically during training. The relative weights of these three components will be selected via a grid search on the validation set, with LPIPS and wavelet loss weighted more heavily to prioritize edge sharpness over raw PSNR, since whiteboard text legibility is fundamentally a perceptual criterion rather than a pixellevel one. Both trained models will be post-training quantized to INT8 using PyTorch’s torch.ao.quantization API with a representative calibration subset of 500 frames drawn from the validation split. The quantized models will then be exported to ONNX format and converted to TensorFlow.js graph models via the ONNX-to-TF bridge, enabling execution in the browser through the TensorFlow.js WebGPU backend. A known risk in this conversion chain is opset incompatibility between PyTorch’s static INT8 quantization and certain ONNX operator versions. If this occurs, the fallback strategy is to perform post-export quantization directly using the ONNX Runtime quantization API before the TF.js conversion step, which bypasses the PyTorch quantization graph entirely. A JavaScript shim will be written using the Insertable Streams API, which is supported natively in Chromium 94 and above. This API intercepts raw video frames from a WebRTC RTCPeerConnection without requiring any modification to the signaling layer. The shim decodes arriving frames, passes them sequentially through the VFI and VSR models, and forwards the upscaled output to the local video compositor. Frame timing is managed through a double-buffer queue to prevent pipeline stalls under variable inference latency. The complete client-side enhancement component will be packaged as a self-contained Chrome browser extension for evaluation purposes. 

The final phase consists of evaluation (Weeks 8 to 10). Evaluation is decomposed into three measurement domains corresponding directly to the three research questions. Each domain has a defined pass criterion established before experimentation begins to prevent post-hoc threshold adjustment. To answer the first research question regarding structural preservation, enhanced test-split frames will be compared against 1080p ground truth using SSIM, VMAF v2.0, and LPIPS. Critically, all three metrics will be computed twice for each clip: once 

over the full frame and once over a masked region of interest cropped to the whiteboard area using a fixed bounding box established per video. This region-of-interest analysis directly isolates whether geometric text structures survive the pipeline, rather than allowing background regions to inflate the overall score. Ablation studies will evaluate four configurations in sequence, including no enhancement, VFI only, VSR only, and the full dual-stage pipeline, to quantify the individual contribution of each stage to the total quality improvement. To answer the second research question regarding latency, end-to-end processing time will be measured as the interval from frame arrival at the JavaScript shim to the frame being committed to the compositor buffer, sampled using performance.now() over 500 consecutive frames. Measurements will be collected on three hardware configurations representing the realistic deployment range, including a mid-range laptop with an Intel Iris Xe iGPU, a budget laptop with an Intel UHD 620, and a desktop with an AMD Radeon Vega 8 integrated GPU. Mean, P95, and P99 latency values will be recorded for each device, and the pass criterion is a P95 latency below 200 ms, consistent with the interactivity threshold established in the related literature. INT8 and FP32 latency will be compared side by side on each device to quantify the practical benefit of quantization independently of architecture changes. To answer the third research question regarding the power and bandwidth trade-off, CPU and GPU power draw during pipeline execution will be sampled at one-second intervals using Intel Power Gadget on Windows and powerstat on Ubuntu. It should be noted that Intel Power Gadget is unsupported on 12thgeneration and newer Intel platforms. For affected devices, Windows power sampling will use the RAPL (Running Average Power Limit) interface via the OpenHardwareMonitor library. On Ubuntu, per-domain iGPU power will be isolated using the intel rapl common kernel module where available. Energy consumption per processed frame in millijoules will be calculated from the sampled wattage and per-frame processing time. This per-frame energy cost will be set against the bandwidth saved by transmitting at 360p and 150 kbps rather than 1080p and 2.5 Mbps, and the result will be reported as an energy-per-saved-kilobit ratio. This single cross-dimensional metric provides a concrete and interpretable answer to whether the local compute cost of client-side enhancement is justified by the reduction in network demand, particularly for batterypowered student devices operating on constrained mobile data plans. By the end of Week 10, the project will have produced four concrete deliverables: a documented whiteboard lecture dataset of approximately 8 hours with matched LR–HR pairs and a reproducible degradation script; two trained and INT8quantized neural models with published checkpoint files; a functional Chrome browser extension implementing the full client-side enhancement pipeline; and a benchmarking report containing all metric tables, latency distributions across hardware tiers, and ablation results. 

If the university GPU lab is unavailable during the training weeks, Google Colab Pro will serve as the primary compute fallback with no change to the training procedure. If the INT8- 

quantized pipeline fails to meet the P95 latency target of 200 ms on the budget Intel UHD 620 hardware tier, the team will reduce the SR model from three residual blocks to two and re-evaluate before considering any further architectural simplification. If the Insertable Streams API produces inconsistent frame timing across Chromium versions during integration testing, evaluation will fall back to an offline simulation in which decoded frames are processed by the pipeline outside the browser and re-encoded for metric computation, preserving the validity of all visual fidelity and latency measurements. 

## X. PROJECT TIMELINE 

The execution of the research phases is planned over a 10week period as detailed in Table II. 

## TABLE II 

DETAILED 10-WEEK CAPSTONE RESEARCH TIMELINE 

## **Week Primary Activities** 

- 1 Lecture recording setup, session planning, and OBS configuration 

- 2 Raw footage capture across all four content domains 3 FFmpeg degradation pipeline, dataset splitting, and storage; VFI fine-tuning begins 

- 4 RIFE fine-tuning, wavelet loss integration, and validation monitoring 

- 5 ESPCN training from scratch and composite loss grid search 6 SR validation and VFI and VSR checkpoint selection 7a INT8 quantization, ONNX export, and TF.js graph model conversion 

- 7b Insertable Streams API integration and initial end-to-end pipeline smoke test 

- 8 Chrome extension integration, end-to-end pipeline testing, and bug resolution 

- 9 Full evaluation across hardware tiers, ablation studies, and ROI metric computation 

- 10 Power profiling, trade-off analysis, report writing, and final submission 

Week 7 represents the highest-risk integration point. A two-day buffer is built into Week 8 to absorb overflow from Week 7 debugging. 

## REFERENCES 

- [1] S. Fouladi, J. Emmons, E. Orbay, C. Wu, R. S. Wahby, and K. Winstein, “Salsify: _{_ Low-Latency _}_ network video through tighter integration between a video codec and a transport protocol,” in _15th USENIX Symposium on Networked Systems Design and Implementation (NSDI 18)_ , 2018, pp. 267–282. 

- [2] S. Liu, “Anvil: Accelerator-native video interpolation via codec motion vector priors,” _arXiv preprint arXiv:2603.26835_ , 2026. 

- [3] M. Fazel and A. Bentaleb, “Vsr-bench: An open-source platform for browser-native real-time vsr evaluation in webrtc,” in _Proceedings of the ACM Multimedia Systems Conference 2026_ , 2026, pp. 450–456. 

- [4] L. Kong, B. Jiang, D. Luo, W. Chu, Y. Tai, C. Wang, and J. Yang, “Dynamic frame interpolation in wavelet domain,” _IEEE Transactions on Image Processing_ , vol. 32, pp. 5296–5309, 2023. 

- [5] L. Kong, B. Jiang, D. Luo, W. Chu, X. Huang, Y. Tai, C. Wang, and J. Yang, “Ifrnet: Intermediate feature refine network for efficient frame interpolation,” in _Proceedings of the IEEE/CVF conference on computer vision and pattern recognition_ , 2022, pp. 1969–1978. 

- [6] R. Zhang, P. Isola, A. A. Efros, E. Shechtman, and O. Wang, “The unreasonable effectiveness of deep features as a perceptual metric,” in _Proceedings of the IEEE conference on computer vision and pattern recognition_ , 2018, pp. 586–595. 

- [7] Z. Geng, L. Liang, T. Ding, and I. Zharkov, “Rstt: Real-time spatial temporal transformer for space-time video super-resolution,” in _Proceedings of the IEEE/CVF conference on computer vision and pattern recognition_ , 2022, pp. 17 441–17 451. 

- [8] M. S. Sajjadi, R. Vemulapalli, and M. Brown, “Frame-recurrent video super-resolution,” in _Proceedings of the IEEE conference on computer vision and pattern recognition_ , 2018, pp. 6626–6634. 

- [9] W. Yang, J. Feng, G. Xie, J. Liu, Z. Guo, and S. Yan, “Video super-resolution based on spatial-temporal recurrent residual networks,” _Computer Vision and Image Understanding_ , vol. 168, pp. 79–92, 2018. 

- [10] N. Fang and Z. Zhan, “High-resolution optical flow and frame-recurrent network for video super-resolution and deblurring,” _Neurocomputing_ , vol. 489, pp. 128–138, 2022. 

- [11] Y. Huang, W. Wang, and L. Wang, “Video super-resolution via bidirectional recurrent convolutional networks,” _IEEE transactions on pattern analysis and machine intelligence_ , vol. 40, no. 4, pp. 1015–1028, 2017. 

- [12] D. Fuoli, S. Gu, and R. Timofte, “Efficient video super-resolution through recurrent latent space propagation,” in _2019 IEEE/CVF International Conference on Computer Vision Workshop (ICCVW)_ . IEEE, 2019, pp. 3476–3485. 

- [13] Y. Wen, C. Zhang, C. Xie, and X. Fu, “Achieving lightweight superresolution for real-time computer graphics,” in _Proceedings of the AAAI Conference on Artificial Intelligence_ , vol. 39, no. 8, 2025, pp. 8313– 8322. 

- [14] X. Yang, W. Xiang, H. Zeng, and L. Zhang, “Real-world video superresolution: A benchmark dataset and a decomposition based learning scheme,” in _Proceedings of the IEEE/CVF international conference on computer vision_ , 2021, pp. 4781–4790. 

- [15] R. Lee, S. I. Venieris, L. Dudziak, S. Bhattacharya, and N. D. Lane, “Mobisr: Efficient on-device super-resolution through heterogeneous mobile processors,” in _The 25th annual international conference on mobile computing and networking_ , 2019, pp. 1–16. 

- [16] S. Hirose, N. Wada, J. Katto, and H. Sun, “Research and examination on implementation of super-resolution models using deep learning with int8 precision,” in _2022 International Conference on Artificial Intelligence in Information and Communication (ICAIIC)_ . IEEE, 2022, pp. 133–137. 

- [17] M. Burhanuddin, “Efficient hardware acceleration techniques for deep learning on edge devices: A comprehensive performance analysis,” _Khwarizmia_ , vol. 2023, pp. 103–112, 2023. 

- [18] T. Tan and G. Cao, “Deep learning video analytics through edge computing and neural processing units on mobile devices,” _IEEE transactions on mobile computing_ , 2021. 

- [19] I. Kwon, J. Li, and M. Prasad, “Lightweight video super-resolution for compressed video,” _Electronics_ , vol. 12, no. 3, p. 660, 2023. 

- [20] A. Rafiei Oskooei, E. Caglar, I. S¸ahin, A. Kayabay, and M. S. Aktas, “Generative ai for video translation: A scalable architecture for multilingual video conferencing,” _Applied Sciences_ , vol. 15, no. 23, p. 12691, 2025. 

- [21] Z. Li, Z.-L. Zhu, L.-H. Han, Q. Hou, C.-L. Guo, and M.-M. Cheng, “Amt: All-pairs multi-field transforms for efficient frame interpolation,” in _Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition_ , 2023, pp. 9801–9810. 

- [22] K. C. Chan, X. Wang, K. Yu, C. Dong, and C. C. Loy, “Basicvsr: The search for essential components in video super-resolution and beyond,” in _Proceedings of the IEEE/CVF conference on computer vision and pattern recognition_ , 2021, pp. 4947–4956. 

- [23] S. Yang, J. Ji, J. Zhuge, J. Zhao, Q. Qiu, C. Li, Y. Yan, K. Wang, L. Yan, and X. Jin, “Lightweight, edge-aware, and temporally consistent supersampling for mobile real-time rendering,” _ACM Transactions on Graphics (TOG)_ , vol. 44, no. 6, pp. 1–12, 2025. 

- [24] M. Fazel and A. Bentaleb, “More pixels, less bandwidth: A live demo of vsr-bench over webrtc,” in _Proceedings of the ACM Multimedia Systems Conference 2026_ , 2026, pp. 333–339. 

- [25] Z. Huang, T. Zhang, W. Heng, B. Shi, and S. Zhou, “Real-time intermediate flow estimation for video frame interpolation,” in _European conference on computer vision_ . Springer, 2022, pp. 624–642. 

- [26] A. Ignatov, A. Romero, H. Kim, and R. Timofte, “Real-time video superresolution on smartphones with deep learning, mobile ai 2021 challenge: Report,” in _Proceedings of the IEEE/CVF conference on computer vision and pattern recognition_ , 2021, pp. 2535–2544. 

- [27] Z. Xiao, X. Fu, J. Huang, Z. Cheng, and Z. Xiong, “Space-time distillation for video super-resolution,” in _Proceedings of the IEEE/CVF conference on computer vision and pattern recognition_ , 2021, pp. 2113– 2122. 

- [28] Y. Zhang, H. Chen, X. Chen, Y. Deng, C. Xu, and Y. Wang, “Data-free knowledge distillation for image super-resolution,” in _Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition_ , 2021, pp. 7852–7861. 

- [29] M. P. Mahenge and J. W. Mwangoka, “Mobile-based system for costeffective e-learning contents delivery in resource and bandwidth constrained learning environments,” _Knowledge Management & E-Learning_ , vol. 6, no. 4, p. 449, 2014. 

- [30] A. M. Vizitiu, M. A. Sandu, L. Dobrescu, A. Focs, a, and C. C. Molder, “Comparative approach to de-noising tempest video frames,” _Sensors_ , vol. 24, no. 19, p. 6292, 2024. 

