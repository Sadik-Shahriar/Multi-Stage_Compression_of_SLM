## **Green Computing** 

Term Project Guidelines & Research Framework 

Instructor: AASR May 21, 2026 

Department of Computer Science and Engineering East West University 

## **Green Computing: Critical Real-World Context** 

**Definition:** Environmentally sustainable computing through energy efficiency, resource optimization, and sustainable Information Technology 

(IT) lifecycle management. **Global Impact — Real Numbers:** 

-  **Information and Communications Technology (ICT):** 2–3% of global CO2, projected at 7–8% by 2030 

-  **Data Centers:** _∼_ 415 Terawatt-hours (TWh)/year — _∼_ 2% of global electricity, doubling by 2030 (IEA, 2024) 

-  **Artificial Intelligence (AI):** GPT-3 training emitted 552 tons of CO2; inference at scale now _exceeds_ that annually 

-  **Bitcoin:** _∼_ 150 TWh/year — comparable to Argentina’s total electricity use 

**Bangladesh Context:** 

-  ICT energy demand growing 15–20% per year; AI-driven data centers add further pressure 

Your Task: Address a REAL, MEASURABLE problem in one trimester 

1 

## **Research Areas & Project Ideas (Part 1)** 

## **1. AI Model Energy Optimization** 

-  **Gap:** Multi-objective optimization for energy-accuracy trade-offs is unsolved; Large Language Models (LLMs) consume massive energy during training and inference 

-  **Try:** Use Non-dominated Sorting Genetic Algorithm II (NSGA-II) for Pareto-optimal model compression — minimizing energy, accuracy loss, and latency together 

## **2. Data Center Workload-Cooling Co-optimization** 

-  **Gap:** Models that optimize workload placement and cooling jointly are rare; cooling accounts for 40% of energy and Power Usage Effectiveness (PUE) often exceeds 1.5 

-  **Try:** Formulate a Linear Programming (LP) model for joint server placement and Computer Room Air Conditioning (CRAC) unit control to minimize total energy 

## **3. Federated Learning (FL) Communication Trade-offs** 

-  **Gap:** Adaptive optimization for the communication-computation balance is missing; 97% of FL carbon comes from client devices 

-  **Try:** Apply Top-K gradient compression ( _k_ =10%) to reduce FL communication energy; measure the accuracy-energy trade-off across 50 devices 

## **4. Edge Computing Task Offloading** 

-  **Gap:** Real-time integer programming for heterogeneous Internet of Things (IoT) environments is lacking 

-  **Try:** Build a binary Integer Programming (IP) model that decides local vs. edge/cloud execution and minimizes total device, network, and server energy 

2 

## **Research Areas & Project Ideas (Part 2)** 

## **5. Renewable Energy-Aware Cloud Scheduling** 

-  **Gap:** Stochastic optimization for carbon-aware scheduling across geo-distributed data centers is rare 

-  **Try:** Implement two-stage stochastic programming; simulate with real solar data from the National Renewable Energy Laboratory (NREL) 

## **6. Blockchain Consensus Energy Reduction** 

-  **Gap:** Energy-efficient alternatives to Proof of Work (PoW) are understudied; PoW consumes _∼_ 150 TWh/year 

-  **Try:** Empirically compare PoW vs. Proof of Stake vs. other consensus mechanisms on energy per confirmed transaction 

## **7. Network Function Virtualization (NFV) Energy Management** 

-  **Gap:** Mixed-Integer Programming (MIP) for joint Virtual Network Function (VNF) placement and traffic routing is rarely studied 

-  **Try:** Formulate a MIP model for VNF consolidation in a 5G core network; compare energy vs. a baseline first-fit allocation 

## **8. Smart Building Heating, Ventilation, and Air Conditioning (HVAC) Optimization** 

-  **Gap:** Model predictive control with Reinforcement Learning (RL) for multi-zone buildings is an open problem; buildings consume 40% of global energy 

-  **Try:** Train an RL agent to schedule HVAC zones based on occupancy forecasts; compare against a rule-based thermostat baseline 

3 

## **Emerging Research Areas & Project Ideas (2024–2025)** 

## **9. LLM Inference Carbon Footprint** 

-  **Gap:** Inference now produces more total carbon than one-time training — yet no standard measurement protocol exists; each AI query uses _∼_ 10 _×_ the energy of a web search 

-  **Try:** Profile energy per output token for several LLMs using CodeCarbon; compare direct-answer vs. chain-of-thought prompting on energy cost 

## **10. Carbon-Aware Workload Scheduling** 

-  **Gap:** Latency and privacy constraints reduce theoretical carbon savings by 60–80% in practice; this theory-to-practice gap is underexplored 

-  **Try:** Build a scheduler that delays batch jobs until grid carbon intensity drops, using the Electricity Maps Application Programming Interface (API) 

## **11. Embodied Carbon in Computing Hardware** 

-  **Gap:** Manufacturing a modern Graphics Processing Unit (GPU) can emit more carbon than running it for three years — public lifecycle data from chip makers is scarce 

-  **Try:** Use the ACT (Architecture Carbon Modeling Tool) to compare lifecycle carbon of different hardware refresh scenarios over 3- and 5-year periods 

## **12. AI Water Footprint** 

-  **Gap:** Water used for data center cooling is almost entirely unmeasured at the model or query level; AI may consume 4–6 billion m[3] /year by 2027 

-  **Try:** Build a per-inference water model as a function of cooling technology and data center location; validate against published facility reports 

4 

## **Research Angles: Optimization-Based Approaches** 

## **Linear Programming (LP):** 

-  Resource allocation in cloud and edge computing 

-  Optimal Virtual Machine (VM) placement to minimize power consumption 

-  Renewable energy-aware workload scheduling 

## **Integer and Mixed-Integer Programming (IP/MIP):** 

-  Server consolidation (ON/OFF decisions) 

-  Task offloading in mobile edge computing 

-  VNF placement in 5G networks 

## **Multi-Objective Optimization:** 

-  Pareto-optimal energy-performance-cost trade-offs 

-  Neural Architecture Search (NAS) for energy-efficient AI 

-  Quality of Service (QoS) vs. energy in wireless networks 

## **Stochastic and Dynamic Optimization:** 

-  Workload prediction under uncertainty 

-  Reinforcement Learning (RL) for adaptive power management 

-  Online algorithms for time-varying renewable energy 

5 

## **Research Angles: Different Technical Backgrounds** 

## **Machine Learning (ML) / AI:** 

-  Model compression using NAS with energy objectives 

-  Quantization-aware training for edge deployment 

-  Adaptive FL with energy-accuracy trade-offs 

## **Systems and Networks:** 

-  Dynamic Voltage and Frequency Scaling (DVFS) optimization algorithms 

-  Container orchestration for minimal energy use 

-  Software-Defined Networking (SDN) for green networking 

## **Data Science:** 

-  Time-series forecasting for power demand 

-  Anomaly detection in energy patterns 

-  Predictive modeling for IoT battery life 

6 

## **Additional Project Ideas** 

## **A. Adaptive Dynamic Voltage and Frequency Scaling (DVFS) with RL** 

-  Train an RL agent to dynamically adjust Central Processing Unit (CPU) frequency based on workload 

-  Compare energy savings against fixed DVFS policies on identical workloads 

## **B. Battery Lifetime Optimization for Wireless Sensor Networks (WSN)** 

-  Formulate duty-cycle scheduling as an optimization problem to maximize network lifetime 

-  Balance data collection frequency against remaining battery capacity across nodes 

## **C. Energy-Efficient Container Migration in Kubernetes** 

-  Use MIP to decide when and where to migrate containers in a cluster 

-  Minimize energy consumption while avoiding Service Level Agreement (SLA) violations 

## **D. Green Network Routing via Min-Cost Flow** 

-  Apply min-cost flow algorithms to route traffic through the most energy-efficient network paths 

-  Compare energy-aware routing against shortest-path routing on real network topologies 

## **E. Software Carbon Intensity (SCI) Measurement Tool** 

-  Implement the ISO/IEC 21031:2024 SCI standard for a web application or ML pipeline 

-  Identify which code paths produce the most carbon per user request 

7 

## **How to Find Your Specific Problem** 

**Step 1: Pick a General Area** (from previous slides) **Step 2: Literature Search** 

-  Search ACM Digital Library, IEEE Xplore, ScienceDirect 

-  Read 25–30 abstracts, then go deep on 10–15 full papers 

- **Step 3: Identify Research Gaps** (read “Limitations” & “Future Work” in papers) 

-  **Context gaps:** Missing studies on edge, mobile, or embedded systems 

-  **Method gaps:** Limited optimization approaches tried 

-  **Scale gaps:** Only simulations, no real-world validation 

-  **Integration gaps:** Solutions that only work in isolation 

**Step 4: Feasibility Check** 

-  Hardware/software access, data availability (4–6 weeks), required skills 

8 

## **Example 1: Renewable Energy-Aware Cloud Scheduling (1/2)** 

## **Literature Finding:** 

-  Most cloud scheduling focuses on performance and cost, not carbon 

-  Cloud providers are pushing for carbon neutrality 

-  Papers note: “Integration of renewable forecasting with scheduling remains an open problem” 

**Identified Gap:** Stochastic optimization models for geo-distributed workload scheduling that maximize renewable energy use while maintaining QoS are rare 

**Research Question:** “How can stochastic programming optimize workload placement across geo-distributed data centers to maximize renewable energy use while meeting latency and availability Service Level Agreements (SLAs)?” 

9 

## **Example 1: Renewable Energy-Aware Cloud Scheduling (2/2)** 

## **Hypotheses:** 

-  **H1:** Renewable-aware scheduling reduces carbon by 30–45% compared to cost-minimal scheduling 

-  **H2:** Two-stage stochastic programming outperforms deterministic approaches under high renewable uncertainty 

-  **H0:** No significant impact on carbon emissions (p _>_ 0.05) 

## **Method:** 

-  Simulate using real solar data from the National Renewable Energy Laboratory (NREL) 

-  Compare stochastic vs. deterministic scheduling algorithms 

## **Expected Outcome:** 

-  Pareto frontier showing the trade-off between carbon and performance 

-  Policy recommendations for cloud providers 

10 

## **Example 2: Multi-Objective Task Offloading (1/2)** 

## **Literature Finding:** 

-  Most IoT offloading studies focus on a single objective (energy OR latency, not both) 

-  Few studies consider heterogeneous edge servers 

-  Gap: “Multi-objective optimization with realistic models is needed” 

**Identified Gap:** Pareto-optimal solutions for IoT task offloading that minimize device energy, edge energy, network energy, AND latency simultaneously are limited 

**Research Question:** “What are the Pareto-optimal task offloading strategies for IoT-edge-cloud systems that minimize total energy and latency under dynamic workloads?” 

11 

## **Example 2: Multi-Objective Task Offloading (2/2)** 

## **Hypotheses:** 

-  **H1:** Hybrid offloading (splitting a task across device and edge) achieves better Pareto optimality than binary (all-or-nothing) offloading 

-  **H2:** Edge processing reduces energy by 40–60% vs. cloud-only, while increasing latency by only 10–15% 

-  **H0:** No difference between hybrid and binary offloading (Wilcoxon test, p _>_ 0.05) 

## **Method:** 

-  Formulate as Mixed-Integer Nonlinear Programming (MINLP) 

-  Solve using NSGA-II to obtain the Pareto frontier 

-  Validate using EdgeCloudSim with realistic workload traces 

**Expected Outcome:** A 3D Pareto frontier and practical design guidelines for practitioners 

12 

## **Formulating Strong Research Questions** 

## **A Strong Research Question Must Have:** 

1. A specific context: which system, at what scale, with what constraints 

2. Measurable variables: Joules, milliseconds, PUE 

3. A comparison: method A vs. method B 

4. A feasible scope: achievable within one trimester 

## **Example: FL Communication Efficiency** 

-  Weak: “How can we make FL more energy efficient?” 

-  Strong: “How does adaptive client selection based on battery level affect total energy consumption and convergence time in cross-device FL with 100–500 Android smartphones?” 

## **Why is the strong version better?** 

It names the system (Android), defines clear variables (battery level, energy, convergence time), states the scale (100–500 devices), and produces measurable outcomes. 

13 

## **More Examples: Weak vs. Strong Research Questions** 

## **Data Center Optimization:** 

-  Weak: “Can optimization reduce energy?” 

-  Strong: “What is the potential energy reduction through joint workload and CRAC optimization using Mixed-Integer Linear Programming (MILP) in a 100-rack data center?” 

## **AI Model Compression:** 

-  Weak: “Does pruning save energy?” 

-  Strong: “How do magnitude pruning, structured pruning, and dynamic sparse training compare in energy per inference, accuracy, and memory footprint when deploying ResNet-50 on a Raspberry Pi 4?” 

14 

## **Formulating Testable Hypotheses** 

## **Hypothesis Structure:** 

-  **H1 (Alternative):** A specific prediction with direction and expected magnitude 

-  **H0 (Null):** No effect — used as the baseline for statistical testing 

## **Example: Container Orchestration** 

-  **H1:** “Energy-aware container placement using bin-packing with DVFS reduces cluster energy by 25–35% compared to the default scheduler, without degrading response time by more than 5%” 

-  **H0:** “No significant difference in energy consumption (paired t-test, _α_ = 0.05)” 

## **What Makes This Strong:** 

-  Gives a quantitative prediction (25–35%) 

-  Names a clear baseline (default scheduler) 

-  Sets a secondary constraint (response time below 5%) 

-  Specifies a testable null hypothesis with a named statistical test 

15 

## **More Hypothesis Examples** 

## **Federated Learning Communication:** 

-  **Gap:** Battery-powered devices need adaptive model update strategies 

-  **H1:** “Gradient compression (Top-K with k = 10%) reduces communication energy by 60–70% while keeping accuracy within 2% of the uncompressed baseline” 

-  **H0:** “No effect on energy consumption (Wilcoxon test, p _>_ 0.05)” 

-  **Validation:** 50 Raspberry Pi devices; INA219 current sensors; 100 FL rounds 

## **Database Query Optimization:** 

-  **Gap:** Energy impact of query design is underexplored 

-  **H1:** “Index-based queries consume 40–50% less energy than full table scans for datasets above 1 million rows, but write overhead negates savings when the write-to-read ratio exceeds 0.3” 

-  **H0:** “No energy difference between query types (Mann-Whitney U test, p _>_ 0.05)” 

16 

## **Statistical Analysis: Choosing the Right Test** 

|**Scenario**|**Test**|**Example**|
|---|---|---|
|2 groups (normal data)|t-test|Algorithm A vs. B|
|2 groups (non-normal)|Mann-Whitney|Method 1 vs. 2|
|Paired samples|Paired t-test|Before vs. After|
|_>_2 groups (normal)|ANOVA + Tukey post-hoc|5 scheduling policies|
|_>_2 groups (non-normal)|Kruskal-Wallis|Multiple frameworks|
|Correlation|Pearson / Spearman|Complexity vs. energy|



ANOVA = Analysis of Variance. Non-parametric tests make no normality assumption. 

## **What to Always Report:** 

-  Test statistic, degrees of freedom, p-value, and effect size 

-  Example: “Paired t-test: t(29) = 5.43, p _<_ 0.001, d = 0.98” 

-  Always check assumptions (normality, equal variance) before choosing a test 

17 

## **Hypothesis Testing: Step-by-Step Workflow** 

1. **State Hypotheses:** Write H1 and H0 clearly _before_ collecting any data 

2. **Set Significance Level:** Use _α_ = 0.05 as the standard threshold 

3. **Collect Data:** Run a power analysis to determine minimum sample size (aim for n _≥_ 30) 

## 4. **Check Assumptions:** 

   -  Normality: Shapiro-Wilk test (if p _<_ 0.05, use a non-parametric test instead) 

   -  Equal variance: Levene’s test 

5. **Run the Test:** Choose parametric or non-parametric based on assumptions 

## 6. **Interpret Results:** 

   -  p _<_ 0.05: Reject H0, results support H1 

   -  p _≥_ 0.05: Fail to reject H0 

7. **Report Effect Size:** Cohen’s d, eta-squared ( _η_[2] ), or Cliff’s delta 

18 

## **Practical Example: Complete Statistical Analysis** 

**Scenario:** Comparing 3 container schedulers in Kubernetes 

**Data:** 3 schedulers _×_ 40 runs = 120 measurements (cluster energy in kilowatt-hours (kWh), over 24 hours each) 

## **Checking Assumptions:** 

-  Shapiro-Wilk: p _>_ 0.05 (data is normal — OK) 

-  Levene’s test: p = 0.12 (equal variance — OK) 

-  _⇒_ Use ANOVA 

## **Analysis Results:** 

-  ANOVA: F(2, 117) = 28.5, p _<_ 0.001, _η_[2] = 0.33 

-  Tukey post-hoc: Energy-Aware (EA) vs. Default (DF): p _<_ 0.001; EA vs. Bin-Packing (BP): p _<_ 0.001 

**Conclusion:** The energy-aware scheduler reduces energy by 32% compared to the default and 28% compared to bin-packing. 

19 

## **Tools for Statistical Analysis** 

## **Python (Recommended):** 

-  `scipy.stats` : t-tests, ANOVA, Mann-Whitney 

-  `statsmodels` : Regression and advanced models 

-  `pingouin` : Effect sizes and power analysis 

**R:** 

-  `t.test()` , `aov()` , `wilcox.test()` 

-  Packages: `car` , `effsize` 

## **Visualization:** 

-  `matplotlib` , `seaborn` 

-  Always show: mean, standard deviation, confidence intervals, and p-values 

## **Sample Size Calculation:** 

-  G*Power (free desktop tool) or `statsmodels.stats.power` 

20 

## **Project Timeline** 

## **Week 1–2: Problem & Proposal** 

-  Literature search (20–30 papers) 

-  Formulate research question and hypotheses 

-  Deliverable: Proposal (5 marks) 

## **Week 3–4: Methodology** 

-  Design experiments or simulation setup 

-  Run a pilot study to catch problems early 

## **Week 5–7: Data Collection and Conducting Experiments** 

-  Run all experiments 

-  If human participants are involved: Signed informed consent is required before data collection begins 

## **Week 8–9: Analysis & Writing** 

-  Statistical analysis and hypothesis testing 

-  Draft results and discussion sections 

**Week 10–11: Final Report** 

21 

## **Course Outcomes: Project Proposal (5 marks)** 

## **Components:** 

-  Introduction & Background 

-  Problem Statement 

-  Research Objectives 

-  Research Questions 

-  Planned Methodology 

-  Expected Results 

## **Marks Distribution:** 

-  Cognitive (C6 - Creating): 3 marks 

-  Affective (A3/A4 - Valuing/Organizing): 0.5 marks 

-  Psychomotor (P3 - Precision): 0.5 marks 

22 

## **Course Outcomes: Final Term Paper (15 marks)** 

## **Components:** 

-  Abstract 

-  Introduction, Background, Problem Statement 

-  Research Questions & Objectives 

-  Methodology 

-  Results & Analysis 

-  Discussion & Conclusion 

## **Marks Distribution:** 

-  Cognitive (C6 - Creating): 10 marks 

-  Affective (A3/A4): 2 marks 

-  Psychomotor (P3): 3 marks 

23 

## **Assessment: Complex Engineering Problems** 

**Your project must address Engineering Problems EP1, EP2, and EP5:** 

## **EP1 — Depth of Knowledge (40%):** 

-  Requires advanced engineering knowledge (K3–K8 level) 

-  Analyze the problem using the specified knowledge profile 

-  Evaluate the problem to propose an effective solution 

## **EP2 — Conflicting Requirements (40%):** 

-  Problem must involve conflicting technical or engineering issues 

-  Compare the conflicting requirements clearly 

-  Propose solution trade-offs and justify your choice 

## **EP5 — Stakeholder Involvement (20%):** 

-  Problem must involve groups with widely different needs 

-  Identify and differentiate the stakeholder groups 

-  Select the requirements that most directly impact the problem 

24 

## **Report Grading Criteria (Part 1)** 

## **U1: Abstract** 

-  150–250 words; must cover: problem, research question, method, results, and conclusion 

## **U2: Introduction** 

-  Enough background for any reader to understand the problem without prior knowledge 

## **U3: Problem Statement** 

-  Clearly stated, of general interest, and backed by at least 3 cited sources 

## **U4: Research Question** 

-  Well-formulated, scoped, derived from the problem, and directly answered in the results 

## **U5: Scientific Base** 

-  In-depth discussion of prior research; a comprehensive literature review 

## **U6: Method Choice** 

-  Justified choice of method; alternatives discussed; ethical considerations 

25 

## **Report Grading Criteria (Part 2)** 

## **U7: Method Application** 

-  Clear description of how methods were applied; depth of analysis demonstrated 

## **U8: Results & Analysis** 

-  High-quality results that directly answer the research question; well-grounded conclusions 

## **U9: Discussion** 

-  Clear answer to the research question; limitations stated; future work suggested; ethical and societal impact discussed 

## **U10: Form & Language** 

-  Logical structure, professional language, fewer than 2 errors per page 

## **U11: Argumentation** 

-  Well-grounded, coherent, and clear; every claim is supported by evidence 

## **U12: Citations** 

-  IEEE or Harvard style; at least 25 scientific references; correct format throughout 

26 

## **Data Collection & Ethics Documentation** 

## **Human Participants (MANDATORY):** 

-  Signed informed consent forms must be collected before any data collection begins 

-  Forms must cover: purpose, procedures, risks/benefits, and confidentiality 

-  Attach consent forms to your report (Appendix 2) 

## **Interviews:** 

-  Audio recordings require written permission from participants 

-  Create verified transcripts from all recordings 

## **Surveys:** 

-  Include the full survey instrument in Appendix 3 

**Technical Studies (No Human Participants):** 

-  Discuss ethical implications: environment, privacy, fairness 

-  Justify in writing if no direct ethical concerns apply 

27 

## **Literature Sources: Top Venues** 

## **Journals:** 

-  IEEE Transactions on Sustainable Computing (Impact Factor (IF): 3.9) 

-  Sustainable Computing: Informatics and Systems (Elsevier) 

-  ACM Transactions on Modeling and Computer Simulation 

-  Journal of Cleaner Production 

-  Cell Patterns — Elsevier (covers AI sustainability, 2023–2025) 

## **Conferences:** 

-  IEEE IGCC — International Green and Sustainable Computing Conference 

-  ACM e-Energy — Future Energy Systems 

-  IEEE GreenCom — Green Communications and Computing 

-  ACM COMPASS — Computing and Sustainable Societies 

-  HotCarbon — ACM Workshop on Sustainable Computer Systems (2022–present) 

## **Workshops (Accessible for Student Projects):** 

-  IGCC and e-Energy workshop tracks 

-  Student research competition tracks 

28 

## **Literature Search Strategy** 

## **Databases:** 

-  ACM Digital Library, IEEE Xplore 

-  ScienceDirect, SpringerLink 

-  Google Scholar (good for a first pass; prefer the above for full 

- papers) 

## **Example Search Strings:** 

-  (“energy efficiency” OR “green computing”) AND “optimization” 

-  “federated learning” AND “energy” AND “mobile” 

-  Apply filters: Last 5 years, peer-reviewed only 

## **Reading Strategy:** 

1. Browse 25–30 abstracts _→_ Select 15 worth reading fully 

2. Read 15 papers _→_ Identify 8–10 core papers 

3. Deep dive into 5–8 key papers 

4. Use Zotero or Mendeley to manage references from the start 

29 

## **Reference Management & Citation** 

**Use a Reference Manager:** 

-  **Zotero** (free, recommended) 

-  **Mendeley** (free) 

-  **EndNote** (paid) 

**Citation Style:** 

-  Choose **IEEE** or **Harvard** — and stay consistent throughout 

-  IEEE: numbered in brackets [1], [2] 

-  Harvard: (Author, Year) in-text 

## **Requirements:** 

-  At least 25 scientific references 

-  Mix foundational papers with recent ones (last 3 years) 

-  Every reference cited in the text must appear in the bibliography, and vice versa 

**Avoid:** Wikipedia and blogs — fine for initial understanding, but cannot be cited as scientific sources 

30 

## **Academic Writing Essentials** 

## **Critical Rules:** 

 **No personal pronouns** in the problem statement 

 ✗ “We believe data centers consume...” 

 ✓ “Data centers consume 1–2% of global electricity [cite]” 

 **Every claim needs support** — a citation or measured data 

-  **Problem statement structure:** 

 Start factual (cite at least 3 papers) 

 Use the phrase: “The problem this research addresses is...” 

 Clearly show the gap in existing literature 

**Be specific, not vague:** 

 ✗ “Energy is a big problem” 

 ✓ “Data centers consume 200 TWh annually [cite]” 

**Proofreading:** Use Grammarly and ask a peer to review your draft 

31 

## **Common Mistakes to Avoid** 

## **Research Design:** 

- ✗ Scope too ambitious 

- ✗ Not testing tools early 

- ✗ No backup plan 

- ✓ Start small, scale up 

- ✓ Run a pilot study first 

## **Writing:** 

- ✗ Fewer than 10 references 

- ✗ Personal opinions without citations 

- ✓ Factual, well-cited prose 

## **Methodology:** 

- ✗ Unjustified method choice 

- ✗ Small sample (n _<_ 30) 

- ✗ No statistical tests 

- ✓ Justify every decision 

- ✓ Run a power analysis first 

## **Results:** 

- ✗ No p-values reported 

- ✗ Poor or missing visualizations 

- ✓ Clear graphs with statistics 

32 

## **What Is Expected: Summary** 

## **Your Paper Must Include:** 

-  A clear abstract (150–250 words) 

-  A well-motivated problem backed by literature 

-  A focused, measurable research question 

-  Testable hypotheses (H1 and H0) 

-  A thorough literature review (at least 10 cited sources in the review) 

-  A justified methodology 

-  Rigorous results with statistical analysis 

-  A critical discussion covering limitations and future work 

-  Proper documentation (IEEE/Harvard citation, consent forms if applicable) 

-  An original contribution to the field 

**Remember:** Weekly instructor meetings _·_ Address EP1, EP2, EP5 _·_ Quality over quantity 

33 

## **Getting Started: Week 1 Action Items** 

## **Week 1 Checklist:** 

1. Pick a general research area from this presentation 

2. Start your literature search: 

   -  Read 20–30 abstracts 

   -  Identify 5–8 core papers to read fully 

3. Identify a specific research gap 

4. Draft your research question (specific and measurable) 

5. Formulate your hypotheses: H1 with a quantitative prediction, and H0 

6. Schedule a meeting with the instructor for approval by Week 3 

Start early — literature search takes longer than expected. 

34 

## **Resources & Support** 

**Literature Databases:** ACM Digital Library, IEEE Xplore, ScienceDirect, SpringerLink 

**Tools:** 

-  References: Zotero, Mendeley 

   - Statistics: Python (scipy, statsmodels), R 

-  Sample Size: G*Power — Writing: Grammarly, Overleaf 

-  Energy Measurement: CodeCarbon, Scaphandre (free, open-source) 

-  Carbon Scheduling: Carbon Aware SDK (Green Software Foundation); Electricity Maps API 

**Templates:** Report template, informed consent form, and rubrics are in the shared course folder. 

**Support:** Weekly instructor meetings — Peer review with classmates 

35 

**Questions?** 

35 

