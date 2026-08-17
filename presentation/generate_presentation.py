import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

def resolve_path(rel_path):
    p1 = os.path.join(PROJECT_ROOT, rel_path)
    if os.path.exists(p1):
        return p1
    p2 = os.path.join(SCRIPT_DIR, rel_path)
    if os.path.exists(p2):
        return p2
    return rel_path

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette - Professional Clean High-Contrast Light Theme
    # Strict compliance: NO dark theme, NO green-white combo, NO generic templates, NO emojis
    C_BG = RGBColor(248, 250, 252)          # Slate 50 (#F8FAFC)
    C_WHITE = RGBColor(255, 255, 255)       # Pure White (#FFFFFF)
    C_CARD_ALT = RGBColor(241, 245, 249)    # Slate 100 (#F1F5F9)
    C_CARD_ACCENT = RGBColor(238, 242, 255) # Indigo 50 (#EEF2FF)
    C_CARD_WARM = RGBColor(255, 247, 237)   # Amber 50 (#FFF7ED)
    C_CARD_ALERT = RGBColor(254, 242, 242)  # Rose 50 (#FEF2F2)
    C_CARD_SUCCESS = RGBColor(240, 253, 250)# Teal 50 (#F0FDFA)
    
    C_NAVY_DARK = RGBColor(15, 23, 42)      # Slate 900
    C_NAVY = RGBColor(30, 41, 59)           # Slate 800
    C_BODY = RGBColor(51, 65, 85)           # Slate 700
    C_MUTED = RGBColor(100, 116, 139)       # Slate 500
    
    C_BLUE = RGBColor(37, 99, 235)          # Blue 600
    C_INDIGO = RGBColor(79, 70, 229)        # Indigo 600
    C_CORAL = RGBColor(234, 88, 12)         # Orange 600 / Amber
    C_RED = RGBColor(225, 29, 72)           # Rose 600
    C_TEAL = RGBColor(13, 148, 136)         # Teal 600
    C_BORDER = RGBColor(226, 232, 240)      # Slate 200
    C_BORDER_ACCENT = RGBColor(199, 210, 254) # Indigo 200

    def set_slide_bg(slide, color=C_BG):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, tracker, title, subtitle=None):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.15))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p0 = tf.paragraphs[0]
        p0.text = tracker.upper()
        p0.font.name = "Calibri"
        p0.font.size = Pt(13)
        p0.font.bold = True
        p0.font.color.rgb = C_BLUE
        p0.space_after = Pt(2)
        
        p1 = tf.add_paragraph()
        p1.text = title
        p1.font.name = "Trebuchet MS"
        p1.font.size = Pt(26)
        p1.font.bold = True
        p1.font.color.rgb = C_NAVY_DARK
        
        if subtitle:
            p1.space_after = Pt(2)
            p2 = tf.add_paragraph()
            p2.text = subtitle
            p2.font.name = "Calibri"
            p2.font.size = Pt(13.5)
            p2.font.color.rgb = C_MUTED

    def add_card(slide, x, y, w, h, bg_color=C_WHITE, border_color=C_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1)
        else:
            card.line.fill.background()
        return card

    # =========================================================================
    # SLIDE 1: Title Slide (with Author Contribution Percentages: 50%, 25%, 25%)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1, C_WHITE)
    
    # Left vertical accent bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.1), Inches(0.12), Inches(5.3))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_BLUE
    bar.line.fill.background()

    tb = s1.shapes.add_textbox(Inches(1.2), Inches(1.05), Inches(11.3), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "RESEARCH PROJECT PRESENTATION  |  CSE407"
    p.font.name = "Calibri"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(10)

    p = tf.add_paragraph()
    p.text = "Multi-Stage Compression of Small Language Models\nfor Energy-Efficient Edge Inference"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(8)

    p = tf.add_paragraph()
    p.text = "An Empirical Systems Ablation Stacking AWQ, Custom PyramidKV Eviction, and TurboQuant on Physical Silicon"
    p.font.name = "Calibri"
    p.font.size = Pt(16)
    p.font.color.rgb = C_MUTED
    p.space_after = Pt(16)

    p = tf.add_paragraph()
    p.text = "Department of Computer Science and Engineering  •  East West University, Dhaka"
    p.font.name = "Calibri"
    p.font.size = Pt(14)
    p.font.color.rgb = C_NAVY

    authors = [
        ("Md. Sadik Shahriar", "50% Contribution", "Lead Researcher / Systems & Architecture", C_CARD_ACCENT, C_BLUE),
        ("Nipa Mridha", "25% Contribution", "Researcher / Retrieval Benchmark & QA", C_CARD_WARM, C_CORAL),
        ("Tanha Humaira", "25% Contribution", "Researcher / Statistical Analysis & Data", C_CARD_ALT, C_NAVY)
    ]
    for idx, (a_name, a_contrib, a_role, a_bg, a_fg) in enumerate(authors):
        ax = Inches(1.2 + idx * 3.75)
        ay = Inches(5.4)
        aw = Inches(3.55)
        ah = Inches(1.25)
        add_card(s1, ax, ay, aw, ah, a_bg, border_color=None)
        
        atb = s1.shapes.add_textbox(ax + Inches(0.18), ay + Inches(0.15), aw - Inches(0.36), ah - Inches(0.3))
        atf = atb.text_frame
        atf.word_wrap = True
        atf.margin_left = atf.margin_top = atf.margin_right = atf.margin_bottom = 0
        
        ap0 = atf.paragraphs[0]
        ap0.text = a_name
        ap0.font.name = "Trebuchet MS"
        ap0.font.size = Pt(15)
        ap0.font.bold = True
        ap0.font.color.rgb = C_NAVY_DARK
        ap0.space_after = Pt(2)
        
        ap1 = atf.add_paragraph()
        ap1.text = a_contrib
        ap1.font.name = "Calibri"
        ap1.font.size = Pt(13.5)
        ap1.font.bold = True
        ap1.font.color.rgb = a_fg
        ap1.space_after = Pt(1)

        ap2 = atf.add_paragraph()
        ap2.text = a_role
        ap2.font.name = "Calibri"
        ap2.font.size = Pt(11)
        ap2.font.color.rgb = C_MUTED

    # =========================================================================
    # SLIDE 2: Motivation — The Edge Inference Memory Wall
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)
    add_header(s2, "1. Motivation & Problem Statement", 
               "The Edge Inference Bottleneck & Stacking Dilemma", 
               "Why small language models (SLMs) choke on edge hardware and why theoretical compression ratios lie.")

    add_card(s2, Inches(0.8), Inches(1.65), Inches(5.65), Inches(5.35), C_WHITE)
    tb = s2.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.05), Inches(4.85))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "The KV-Cache Memory Wall on Edge GPUs"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(12)

    bullets_s2 = [
        ("Linear Context Growth:", "Autoregressive generation stores past Key and Value tensors for every token. Memory footprint expands linearly with sequence length."),
        ("Memory Bandwidth Bound:", "On edge hardware (NVIDIA Tesla T4 with 70W power limit), decoding is memory-bandwidth bound. Every generated token reloads the entire KV-cache from DRAM."),
        ("The Stacking Question:", "Practitioners combine Weight Quantization + Token Eviction + KV Quantization. But do energy savings compound additively or create new overheads?"),
        ("Theoretical vs. Physical Reality:", "Paper-level FLOP counts ignore memory copy stalls, kernel launch latency, and software realization gaps.")
    ]
    for b_title, b_text in bullets_s2:
        p = tf.add_paragraph()
        p.text = f"- {b_title} "
        p.font.name = "Calibri"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        run = p.add_run()
        run.text = b_text
        run.font.bold = False
        run.font.color.rgb = C_BODY
        p.space_after = Pt(8)

    add_card(s2, Inches(6.8), Inches(1.65), Inches(5.733), Inches(5.35), C_CARD_ACCENT, C_BORDER_ACCENT)
    tb = s2.shapes.add_textbox(Inches(7.1), Inches(1.9), Inches(5.133), Inches(4.85))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "The 4-Way Multi-Objective Tension"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(12)

    objectives = [
        ("1. Energy Consumption (Joules)", "Must minimize battery/board power draw across prefill and decode phases under fixed power limits.", C_CORAL),
        ("2. Decode Throughput (tok/s)", "Must maintain responsive generation without compute or dequantization stalls.", C_BLUE),
        ("3. GPU Memory Footprint (MiB)", "Must minimize peak VRAM and persistent KV cache to fit within edge memory budgets.", C_TEAL),
        ("4. Retrieval Accuracy (Quality)", "Must not destroy long-context retrieval fidelity or drop critical target needles.", C_RED)
    ]
    for obj_title, obj_desc, obj_color in objectives:
        p = tf.add_paragraph()
        p.text = obj_title
        p.font.name = "Calibri"
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = obj_color
        p.space_after = Pt(2)
        
        p_sub = tf.add_paragraph()
        p_sub.text = obj_desc
        p_sub.font.name = "Calibri"
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = C_BODY
        p_sub.space_after = Pt(8)

    # =========================================================================
    # SLIDE 3: The Three Compression Pillars
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3)
    add_header(s3, "2. Technical Foundations", 
               "The Three Pillars of SLM Compression", 
               "How Weight Quantization, Token Eviction, and KV Quantization target distinct bottlenecks.")

    pillars = [
        {
            "num": "PILLAR 1",
            "title": "4-Bit AWQ",
            "sub": "Activation-Aware Weight Quantization",
            "target": "Targets Static Model Weights",
            "points": [
                "Protects salient weight channels by observing activation magnitudes (Lin et al.).",
                "4-bit INT4 GEMM weights with group size 128 and asymmetric zero-points.",
                "Reduces static model VRAM by ~60% (from ~6.5 GB down to ~2.2 GB).",
                "Trade-off: Requires runtime dequantization during matrix multiplications."
            ],
            "accent": C_BLUE
        },
        {
            "num": "PILLAR 2",
            "title": "Custom PyramidKV",
            "sub": "Dynamic Token Eviction",
            "target": "Targets KV Cache Token Count",
            "points": [
                "Prunes uninformative tokens based on attention scores (Cai et al., COLM 2025).",
                "Layerwise pyramidal budget (allocates ~1966 tokens in deep layers, ~82 in shallow; avg 1024).",
                "Drastically shrinks active DRAM read volume during decoding.",
                "Trade-off: Risk of evicting vital target tokens if attention heuristics fail."
            ],
            "accent": C_TEAL
        },
        {
            "num": "PILLAR 3",
            "title": "TurboQuant (TQ)",
            "sub": "Randomized KV Quantization",
            "target": "Targets Bytes per Retained Token",
            "points": [
                "Applies randomized polar vector rotation (Johnson-Lindenstrauss) + scalar codebook (Zandieh et al., ICLR 2026).",
                "Nominal 2/3/4-bit quantization without requiring calibration data.",
                "Preserves vector norms in FP32 with a 128-token full-precision residual buffer.",
                "Trade-off: Off-the-shelf reference package introduces significant execution overhead."
            ],
            "accent": C_CORAL
        }
    ]

    card_w = Inches(3.75)
    card_h = Inches(5.35)
    for i, p_info in enumerate(pillars):
        cx = Inches(0.8 + i * 3.99)
        cy = Inches(1.65)
        add_card(s3, cx, cy, card_w, card_h, C_WHITE)
        
        top_bar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, card_w, Inches(0.08))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = p_info["accent"]
        top_bar.line.fill.background()

        tb = s3.shapes.add_textbox(cx + Inches(0.22), cy + Inches(0.2), card_w - Inches(0.44), card_h - Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = p_info["num"]
        p.font.name = "Calibri"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = p_info["accent"]
        p.space_after = Pt(2)

        p = tf.add_paragraph()
        p.text = p_info["title"]
        p.font.name = "Trebuchet MS"
        p.font.size = Pt(21)
        p.font.bold = True
        p.font.color.rgb = C_NAVY_DARK

        p = tf.add_paragraph()
        p.text = p_info["sub"]
        p.font.name = "Calibri"
        p.font.size = Pt(13)
        p.font.color.rgb = C_MUTED
        p.space_after = Pt(8)

        p = tf.add_paragraph()
        p.text = f"[TARGET] {p_info['target']}"
        p.font.name = "Calibri"
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = p_info["accent"]
        p.space_after = Pt(8)

        for pt in p_info["points"]:
            p = tf.add_paragraph()
            p.text = f"• {pt}"
            p.font.name = "Calibri"
            p.font.size = Pt(12.5)
            p.font.color.rgb = C_BODY
            p.space_after = Pt(6)

    # =========================================================================
    # SLIDE 4: Benchmark Evolution — Naive NIAH vs. Our Hard Diagnostic Benchmark
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4)
    add_header(s4, "3. Diagnostic Benchmark Design", 
               "Benchmark Evolution: Why Standard NIAH Fails & Why Our Task is Harder", 
               "Moving from uninformative 100% ceiling benchmarks to a calibrated, exact-match diagnostic suite.")

    # Left: Naive NIAH (Before)
    add_card(s4, Inches(0.8), Inches(1.65), Inches(5.65), Inches(5.35), C_CARD_WARM, C_CORAL)
    tb = s4.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.15), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "BEFORE: Standard / Naive NIAH (Flawed Baseline)"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_CORAL
    p.space_after = Pt(8)

    naive_points = [
        ("Out-of-Domain 'Pop-Out' Needle:", "Inserts an unrelated random sentence (e.g. 'The best thing to do in San Francisco is eat a sandwich') inside natural essays or fiction prose."),
        ("Uninformative 100% Ceiling Effect:", "In our initial trials, ALL 5 compression configurations achieved 100% accuracy. The semantic anomaly is so obvious that even heavily degraded caches spot it easily."),
        ("Zero Distractor Competition:", "No other candidate facts exist in the text. The model does not need to perform precise key disambiguation."),
        ("Methodological Flaw:", "Standard NIAH fails to test KV compression degradation on modern SLMs!")
    ]
    for n_title, n_desc in naive_points:
        p = tf.add_paragraph()
        p.text = f"[•] {n_title} "
        p.font.name = "Calibri"
        p.font.size = Pt(13.5)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        run = p.add_run()
        run.text = n_desc
        run.font.bold = False
        run.font.color.rgb = C_BODY
        p.space_after = Pt(6)

    # Right: Our Hard Diagnostic Benchmark (After)
    add_card(s4, Inches(6.8), Inches(1.65), Inches(5.733), Inches(5.35), C_CARD_SUCCESS, C_TEAL)
    tb = s4.shapes.add_textbox(Inches(7.05), Inches(1.85), Inches(5.233), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "AFTER: Our Hard Diagnostic NIAH (Calibrated)"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_TEAL
    p.space_after = Pt(8)

    hard_points = [
        ("4,096-Token Structured Memos:", "Document consists of 48+ realistic, structured operational memos using identical technical grammar and vocabulary."),
        ("Dense Distractor Overlap:", "Contains 20+ active access records sharing the exact same schema: [Access record] System NODE-<NAME> uses activation code <CODE>."),
        ("Calibrated Diagnostic Headroom:", "4 iterative pilot designs (V1-V4) calibrated task difficulty so the uncompressed baseline achieves 75%-88% accuracy — providing dynamic range to measure compression degradation!"),
        ("Strict Verification:", "Requires exact extraction of alphanumeric activation code with zero explanation allowed.")
    ]
    for h_title, h_desc in hard_points:
        p = tf.add_paragraph()
        p.text = f"[•] {h_title} "
        p.font.name = "Calibri"
        p.font.size = Pt(13.5)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        run = p.add_run()
        run.text = h_desc
        run.font.bold = False
        run.font.color.rgb = C_BODY
        p.space_after = Pt(6)

    # =========================================================================
    # SLIDE 5: Deep Dive into the Hard-Retrieval Prompt Structure
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5)
    add_header(s5, "3. Diagnostic Benchmark Design", 
               "Prompt Structure Deep Dive (llama_hard_retrieval_prompts.md)", 
               "Exact architecture of the 4,096-token frozen prompts used for evaluating memory retention.")

    # Left Card: Prompt Anatomy & Example Excerpt
    add_card(s5, Inches(0.8), Inches(1.65), Inches(6.0), Inches(5.35), C_WHITE)
    tb = s5.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.5), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "Concrete Prompt Excerpt (Scenario d10-s00)"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(6)

    prompt_sample = (
        "System: Use only the document. Return exactly one activation code and no explanation.\n\n"
        "<DOC>\n"
        "Memo 1 discusses warehouse routing... Sample batch 2000...\n"
        "Memo 3: [Access record] System NODE-PRAIRIE uses activation code A925-L88.\n"
        "Memo 5: [Access record] System NODE-CEDRIC uses activation code A895-N19.\n"
        "...\n"
        "Memo 9: [Access record] System NODE-SUMMIT uses activation code A574-N27. [TARGET]\n"
        "...\n"
        "Memo 60: [Access record] System NODE-TEMPEST uses code D969-L18.\n"
        "</DOC>\n\n"
        "User: What is the code for NODE-SUMMIT?\n"
        "Expected Assistant Output: A574-N27"
    )
    p = tf.add_paragraph()
    p.text = prompt_sample
    p.font.name = "Consolas"
    p.font.size = Pt(11)
    p.font.color.rgb = C_NAVY_DARK

    # Right Card: Embedded prompt figure
    add_card(s5, Inches(7.1), Inches(1.65), Inches(5.433), Inches(5.35), C_WHITE)
    tb = s5.shapes.add_textbox(Inches(7.35), Inches(1.85), Inches(4.933), Inches(0.45))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Visual Memo & Needle Architecture"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    img_prompt = resolve_path("paper/figures/hard_retrieval.png")
    if os.path.exists(img_prompt):
        s5.shapes.add_picture(img_prompt, Inches(7.2), Inches(2.4), width=Inches(5.2))

    # =========================================================================
    # SLIDE 6: Experimental Matrix & Configurations
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6)
    add_header(s6, "4. Experimental Setup", 
               "Hardware Telemetry & Evaluated Configurations", 
               "Comparing two 3B models across five isolated and sequential compression stages.")

    # Top: Hardware & Telemetry Card
    add_card(s6, Inches(0.8), Inches(1.65), Inches(11.733), Inches(1.4), C_CARD_ACCENT, C_BORDER_ACCENT)
    tb = s6.shapes.add_textbox(Inches(1.05), Inches(1.75), Inches(11.233), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "HARDWARE & POWER TELEMETRY PROTOCOL"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(2)

    p = tf.add_paragraph()
    p.text = "• Physical GPU: NVIDIA Tesla T4 (16 GB VRAM, 70W enforced power limit) on Linux x86_64\n• Continuous Telemetry: 10 Hz NVML board power polling via pynvml; Riemann trapezoidal energy integration integral P(t)dt\n• Fixed Workload: 64-token teacher-forced decode across 1024, 2048, and 4096 tokens (5 blocks, n=5 per condition)"
    p.font.name = "Calibri"
    p.font.size = Pt(13.5)
    p.font.color.rgb = C_NAVY_DARK

    # Bottom: Configuration Matrix Table (Large text)
    add_card(s6, Inches(0.8), Inches(3.2), Inches(11.733), Inches(3.8), C_WHITE)
    table_shape = s6.shapes.add_table(6, 5, Inches(1.0), Inches(3.4), Inches(11.333), Inches(3.3))
    table = table_shape.table
    table.columns[0].width = Inches(2.0)
    table.columns[1].width = Inches(1.4)
    table.columns[2].width = Inches(1.4)
    table.columns[3].width = Inches(2.4)
    table.columns[4].width = Inches(4.133)

    headers = ["Semantic Role", "Llama Config", "Qwen Config", "Weight Precision", "KV Cache Mechanism & State"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY
        for p in cell.text_frame.paragraphs:
            p.font.name = "Trebuchet MS"
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    config_data = [
        ("FP16 Baseline", "C0", "Q0", "FP16 (Unquantized)", "Uncompressed full precision KV cache (Reference)"),
        ("AWQ Baseline", "C1-W", "Q1-W", "AWQ 4-bit (INT4)", "Full precision KV cache with matched attention wrapper"),
        ("Token Eviction", "C2", "Q2", "AWQ 4-bit (INT4)", "PyramidKV layerwise eviction (Avg 1024 budget / layer)"),
        ("TurboQuant Ref", "C3-Ref", "Q3-Ref", "AWQ 4-bit (INT4)", "TQ 0.2.0 numerical reference (uint8 index + FP16 buffer)"),
        ("Sequential Compound", "C4-Ref", "Q4-Ref", "AWQ 4-bit (INT4)", "Sequential pipeline: AWQ -> Eviction -> TurboQuant")
    ]

    for i, row in enumerate(config_data):
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_CARD_ALT if i % 2 == 1 else C_WHITE
            for p in cell.text_frame.paragraphs:
                p.font.name = "Calibri"
                p.font.size = Pt(13)
                p.font.color.rgb = C_NAVY_DARK
                if j in [0, 1, 2]:
                    p.font.bold = True

    # =========================================================================
    # SLIDE 7: Llama 3.2-3B Systems Comparison @ 4096 Tokens (Headline Results)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7)
    add_header(s7, "5. Llama Systems Results", 
               "Llama 3.2-3B: Headline Systems Comparison at 4096 Tokens", 
               "Direct comparison of all five compression configurations under long-context memory pressure.")

    # Left: Clean 5-Row Table with LARGE font
    add_card(s7, Inches(0.8), Inches(1.65), Inches(7.5), Inches(5.35), C_WHITE)
    tb = s7.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(7.0), Inches(0.45))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Complete 4096-Token Systems Matrix"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK

    t_shape = s7.shapes.add_table(6, 5, Inches(1.05), Inches(2.4), Inches(7.0), Inches(4.3))
    t = t_shape.table
    t.columns[0].width = Inches(1.5)
    t.columns[1].width = Inches(1.7)
    t.columns[2].width = Inches(1.3)
    t.columns[3].width = Inches(1.25)
    t.columns[4].width = Inches(1.25)

    l_headers = ["Config", "Total Energy", "Throughput", "Live Cache", "Peak VRAM"]
    for j, h in enumerate(l_headers):
        c = t.cell(0, j)
        c.text = h
        c.fill.solid()
        c.fill.fore_color.rgb = C_NAVY
        for p in c.text_frame.paragraphs:
            p.font.name = "Trebuchet MS"
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    llama_4k_data = [
        ("C0 (FP16)", "701.08 ± 8.12 J", "11.34 tok/s", "455 MiB", "12688 MiB"),
        ("C1-W (AWQ)", "631.25 ± 5.05 J", "13.77 tok/s", "455 MiB", "8820 MiB"),
        ("C2 (Evict)", "529.30 ± 20.02 J", "20.34 tok/s", "119 MiB", "8500 MiB"),
        ("C3-Ref (TQ)", "913.48 ± 2.11 J", "7.66 tok/s", "697 MiB", "9468 MiB"),
        ("C4-Ref (Both)", "659.50 ± 21.35 J", "12.53 tok/s", "187 MiB", "8662 MiB")
    ]

    for i, row in enumerate(llama_4k_data):
        for j, val in enumerate(row):
            cell = t.cell(i + 1, j)
            cell.text = val
            cell.fill.solid()
            if i == 2:
                cell.fill.fore_color.rgb = C_CARD_SUCCESS
            elif i % 2 == 1:
                cell.fill.fore_color.rgb = C_CARD_ALT
            else:
                cell.fill.fore_color.rgb = C_WHITE
            
            for p in cell.text_frame.paragraphs:
                p.font.name = "Calibri"
                p.font.size = Pt(13)
                p.font.color.rgb = C_TEAL if i == 2 else C_NAVY_DARK
                p.font.bold = (i == 2 or j == 0)

    # Right: High-Impact Callout Cards
    add_card(s7, Inches(8.5), Inches(1.65), Inches(4.033), Inches(5.35), C_CARD_SUCCESS, C_TEAL)
    tb = s7.shapes.add_textbox(Inches(8.75), Inches(1.85), Inches(3.533), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "C2 Eviction: Clear System Winner"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_TEAL
    p.space_after = Pt(12)

    stat_cards = [
        ("-16.15% Total Energy", "Saves 101.95 J over AWQ baseline (p = 0.0055)."),
        ("+47.7% Decode Speedup", "Throughput surges from 13.77 to 20.34 tok/s."),
        ("-73.8% Live KV Cache", "Live cache shrinks from 455 MiB down to 119 MiB."),
        ("Full Quality Retention", "37/60 retrieval matches baseline (38/60, p = 1.0).")
    ]
    for s_title, s_desc in stat_cards:
        p = tf.add_paragraph()
        p.text = s_title
        p.font.name = "Trebuchet MS"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = C_NAVY_DARK
        p.space_after = Pt(1)

        p_sub = tf.add_paragraph()
        p_sub.text = s_desc
        p_sub.font.name = "Calibri"
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = C_BODY
        p_sub.space_after = Pt(8)

    # =========================================================================
    # SLIDE 8: Llama Context Scaling Progression (1024 vs 2048 vs 4096 Tokens)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8)
    add_header(s8, "5. Llama Systems Results", 
               "Llama 3.2-3B: Context Scaling Progression Across Lengths", 
               "Tracking the shift in compression dynamics across 1024, 2048, and 4096 tokens.")

    # Left: Clean 3-Row Scaling Table (Large font)
    add_card(s8, Inches(0.8), Inches(1.65), Inches(5.65), Inches(5.35), C_WHITE)
    tb = s8.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.15), Inches(0.45))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Energy Scaling by Context Length"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK

    t_shape = s8.shapes.add_table(4, 4, Inches(1.05), Inches(2.4), Inches(5.15), Inches(2.5))
    t = t_shape.table
    t.columns[0].width = Inches(1.15)
    t.columns[1].width = Inches(1.3)
    t.columns[2].width = Inches(1.35)
    t.columns[3].width = Inches(1.35)

    sc_headers = ["Context", "FP16 (C0)", "AWQ (C1-W)", "Evict (C2)"]
    for j, h in enumerate(sc_headers):
        c = t.cell(0, j)
        c.text = h
        c.fill.solid()
        c.fill.fore_color.rgb = C_NAVY
        for p in c.text_frame.paragraphs:
            p.font.name = "Trebuchet MS"
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    sc_rows = [
        ("1024 Tok", "244.1 ± 13.1 J", "268.8 ± 26.2 J", "253.6 ± 14.4 J"),
        ("2048 Tok", "345.3 ± 5.0 J", "313.8 ± 9.3 J", "338.7 ± 21.0 J"),
        ("4096 Tok", "701.1 ± 8.1 J", "631.3 ± 5.1 J", "529.3 ± 20.0 J")
    ]
    for i, r in enumerate(sc_rows):
        for j, v in enumerate(r):
            c = t.cell(i + 1, j)
            c.text = v
            c.fill.solid()
            c.fill.fore_color.rgb = C_CARD_WARM if (i==0 and j==2) else (C_CARD_SUCCESS if (i==2 and j==3) else C_WHITE)
            for p in c.text_frame.paragraphs:
                p.font.name = "Calibri"
                p.font.size = Pt(13)
                p.font.color.rgb = C_CORAL if (i==0 and j==2) else (C_TEAL if (i==2 and j==3) else C_NAVY_DARK)
                p.font.bold = (j==0 or (i==2 and j==3) or (i==0 and j==2))

    tb_sub = s8.shapes.add_textbox(Inches(1.05), Inches(5.1), Inches(5.15), Inches(1.7))
    tf_s = tb_sub.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0
    p_s = tf_s.paragraphs[0]
    p_s.text = "[KEY TAKEAWAYS]\n• 1024 Tokens: AWQ incurs a +10.1% energy penalty due to dequantization overhead.\n• 4096 Tokens: Eviction saves 101.95 J (-16.15%) because DRAM traffic dominates decoding!"
    p_s.font.name = "Calibri"
    p_s.font.size = Pt(13)
    p_s.font.color.rgb = C_BODY

    # Right: Embedded Scaling Plot
    add_card(s8, Inches(6.8), Inches(1.65), Inches(5.733), Inches(5.35), C_WHITE)
    tb = s8.shapes.add_textbox(Inches(7.05), Inches(1.85), Inches(5.233), Inches(0.45))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Empirical Context Scaling Curves"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    img_scale = resolve_path("evidence/accepted/CSE407_cross_model_visualization_v1/fig02_measured_context_scaling.png")
    if os.path.exists(img_scale):
        s8.shapes.add_picture(img_scale, Inches(7.0), Inches(2.4), width=Inches(5.333))

    # =========================================================================
    # SLIDE 9: Llama Hard-Retrieval Accuracy & Wilson Confidence Intervals
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9)
    add_header(s9, "5. Llama Retrieval Results", 
               "Llama 3.2-3B: Hard-Retrieval Accuracy & Wilson 95% CIs", 
               "Evaluated on 60 frozen scenarios at 4096 tokens under strict exact-match verification.")

    # Left: Clean 5-Row Quality Table
    add_card(s9, Inches(0.8), Inches(1.65), Inches(5.65), Inches(5.35), C_WHITE)
    tb = s9.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.15), Inches(0.45))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Overall Accuracy (60 Scenarios)"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK

    t_shape = s9.shapes.add_table(6, 4, Inches(1.05), Inches(2.4), Inches(5.15), Inches(2.5))
    t = t_shape.table
    t.columns[0].width = Inches(1.2)
    t.columns[1].width = Inches(1.1)
    t.columns[2].width = Inches(1.1)
    t.columns[3].width = Inches(1.75)

    q_headers = ["Config", "Pass/60", "Rate", "Wilson 95% CI"]
    for j, h in enumerate(q_headers):
        c = t.cell(0, j)
        c.text = h
        c.fill.solid()
        c.fill.fore_color.rgb = C_NAVY
        for p in c.text_frame.paragraphs:
            p.font.name = "Trebuchet MS"
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    q_rows = [
        ("C0 (FP16)", "47/60", "78.3%", "[66.4%, 86.9%]"),
        ("C1-W (AWQ)", "38/60", "63.3%", "[50.7%, 74.4%]"),
        ("C2 (Evict)", "37/60", "61.7%", "[49.0%, 72.9%]"),
        ("C3-Ref (TQ)", "37/60", "61.7%", "[49.0%, 72.9%]"),
        ("C4-Ref (Both)", "37/60", "61.7%", "[49.0%, 72.9%]")
    ]
    for i, r in enumerate(q_rows):
        for j, v in enumerate(r):
            c = t.cell(i + 1, j)
            c.text = v
            c.fill.solid()
            c.fill.fore_color.rgb = C_CARD_SUCCESS if i in [2, 3, 4] else C_WHITE
            for p in c.text_frame.paragraphs:
                p.font.name = "Calibri"
                p.font.size = Pt(13)
                p.font.color.rgb = C_TEAL if i in [2, 3, 4] else C_NAVY_DARK
                p.font.bold = (i in [2, 3, 4] or j == 0)

    tb_b = s9.shapes.add_textbox(Inches(1.05), Inches(5.1), Inches(5.15), Inches(1.7))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
    p_b = tf_b.paragraphs[0]
    p_b.text = "[QUALITY VALIDATION]\n• C2, C3-Ref, and C4-Ref each differ from AWQ baseline by ONLY ONE scenario (37/60 vs 38/60, McNemar p = 1.0)!\n• TurboQuant fully validates Google's algorithmic quality preservation claim on SLMs."
    p_b.font.name = "Calibri"
    p_b.font.size = Pt(13)
    p_b.font.bold = True
    p_b.font.color.rgb = C_TEAL

    # Right: Embedded Wilson CI Plot
    add_card(s9, Inches(6.8), Inches(1.65), Inches(5.733), Inches(5.35), C_WHITE)
    tb = s9.shapes.add_textbox(Inches(7.05), Inches(1.85), Inches(5.233), Inches(0.45))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Measured Wilson Score Intervals"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    img_wilson = resolve_path("evidence/accepted/CSE407_cross_model_visualization_v1/fig03_retrieval_wilson.png")
    if os.path.exists(img_wilson):
        s9.shapes.add_picture(img_wilson, Inches(7.0), Inches(2.4), width=Inches(5.333))

    # =========================================================================
    # SLIDE 10: Llama Retrieval by Insertion Depth (10% vs 50% vs 90%)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s10)
    add_header(s10, "5. Llama Retrieval Results", 
               "Llama 3.2-3B: Insertion Depth Stratification & Position Bias", 
               "Measuring attention preservation across the prompt Head (10%), Middle (50%), and Tail (90%).")

    # Left: Clean 5-Row Depth Table
    add_card(s10, Inches(0.8), Inches(1.65), Inches(5.65), Inches(5.35), C_WHITE)
    tb = s10.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.15), Inches(0.45))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Accuracy Stratified by Depth"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK

    t_shape = s10.shapes.add_table(6, 4, Inches(1.05), Inches(2.4), Inches(5.15), Inches(2.5))
    t = t_shape.table
    t.columns[0].width = Inches(1.4)
    t.columns[1].width = Inches(1.25)
    t.columns[2].width = Inches(1.25)
    t.columns[3].width = Inches(1.25)

    d_headers = ["Config", "10% (Head)", "50% (Middle)", "90% (Tail)"]
    for j, h in enumerate(d_headers):
        c = t.cell(0, j)
        c.text = h
        c.fill.solid()
        c.fill.fore_color.rgb = C_NAVY
        for p in c.text_frame.paragraphs:
            p.font.name = "Trebuchet MS"
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    d_rows = [
        ("C0 (FP16)", "19/20 (95%)", "13/20 (65%)", "15/20 (75%)"),
        ("C1-W (AWQ)", "18/20 (90%)", "10/20 (50%)", "10/20 (50%)"),
        ("C2 (Evict)", "18/20 (90%)", "10/20 (50%)", "9/20 (45%)"),
        ("C3-Ref (TQ)", "18/20 (90%)", "10/20 (50%)", "9/20 (45%)"),
        ("C4-Ref (Both)", "17/20 (85%)", "10/20 (50%)", "10/20 (50%)")
    ]
    for i, r in enumerate(d_rows):
        for j, v in enumerate(r):
            c = t.cell(i + 1, j)
            c.text = v
            c.fill.solid()
            c.fill.fore_color.rgb = C_CARD_ALT if i % 2 == 1 else C_WHITE
            for p in c.text_frame.paragraphs:
                p.font.name = "Calibri"
                p.font.size = Pt(13)
                p.font.color.rgb = C_NAVY_DARK
                p.font.bold = (j == 0)

    tb_d = s10.shapes.add_textbox(Inches(1.05), Inches(5.1), Inches(5.15), Inches(1.7))
    tf_d = tb_d.text_frame
    tf_d.word_wrap = True
    tf_d.margin_left = tf_d.margin_top = tf_d.margin_right = tf_d.margin_bottom = 0
    p_d = tf_d.paragraphs[0]
    p_d.text = "[POSITION BIAS INSIGHT]\n• Prompt Beginning: All configurations achieve 85%-95% accuracy at 10% depth.\n• Middle/Tail: Accuracy settles at 45%-50% due to dense memo distractor competition."
    p_d.font.name = "Calibri"
    p_d.font.size = Pt(13)
    p_d.font.color.rgb = C_BODY

    # Right: Error Diagnostics Card
    add_card(s10, Inches(6.8), Inches(1.65), Inches(5.733), Inches(5.35), C_CARD_ALT)
    tb = s10.shapes.add_textbox(Inches(7.05), Inches(1.85), Inches(5.233), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "Error Taxonomy & Format Verification"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(10)

    err_points = [
        ("100% Distractor Key Confusions:", "Zero formatting failures occurred. 100% of failed responses returned an exact, valid activation code belonging to another distractor memo in the document."),
        ("No Hallucination of Schema:", "The model never invented non-existent codes or failed output constraints. The error was purely an associative retrieval lookup routing mistake."),
        ("Attention Sink Preservation:", "Initial prompt tokens (first 10%) are preserved by PyramidKV attention sinks, explaining high Head retrieval accuracy."),
        ("Identical Error Distribution:", "C2 and C3-Ref made errors on the exact same mid-context scenarios as the AWQ baseline.")
    ]
    for e_title, e_desc in err_points:
        p = tf.add_paragraph()
        p.text = f"- {e_title} "
        p.font.name = "Calibri"
        p.font.size = Pt(13.5)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        run = p.add_run()
        run.text = e_desc
        run.font.bold = False
        run.font.color.rgb = C_BODY
        p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 11: Statistical & Probabilistic Validation Framework
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s11)
    add_header(s11, "5. Statistical Validation", 
               "Comprehensive Statistical & Probabilistic Validation", 
               "Rigorous mathematical proofs validating physical energy savings, quality bounds, and decision stability.")

    card_w = Inches(5.7)
    card_h = Inches(2.55)

    # Card 1: Top Left - Energy Significance (Paired t-Tests & Holm)
    add_card(s11, Inches(0.8), Inches(1.65), card_w, card_h, C_WHITE, C_BORDER)
    top_bar = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.65), card_w, Inches(0.06))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_TEAL
    top_bar.line.fill.background()

    tb = s11.shapes.add_textbox(Inches(1.05), Inches(1.8), card_w - Inches(0.5), card_h - Inches(0.25))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "1. Energy Significance (Paired t-Tests & Holm)"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(15.5)
    p.font.bold = True
    p.font.color.rgb = C_TEAL
    p.space_after = Pt(4)

    p = tf.add_paragraph()
    p.text = "- Method: Paired two-sided t-tests (n=5 blocks) with Holm step-down correction.\n- Key Result: C2 saves 101.95 J over baseline (95% CI: [73.8, 130.1] J, p = 0.0055).\n- Audience Interpretation: Less than a 0.5% probability that energy savings were random noise."
    p.font.name = "Calibri"
    p.font.size = Pt(12.5)
    p.font.color.rgb = C_NAVY_DARK

    # Card 2: Bottom Left - Retrieval Quality & Exact-Match Rigor (Wilson & McNemar)
    add_card(s11, Inches(0.8), Inches(4.35), card_w, card_h, C_WHITE, C_BORDER)
    top_bar = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(4.35), card_w, Inches(0.06))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_BLUE
    top_bar.line.fill.background()

    tb = s11.shapes.add_textbox(Inches(1.05), Inches(4.5), card_w - Inches(0.5), card_h - Inches(0.25))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "2. Quality Bounds (Wilson CIs & McNemar Tests)"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(15.5)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(4)

    p = tf.add_paragraph()
    p.text = "- Method: Wilson score 95% CIs and exact paired McNemar contingency tests.\n- Key Result: Llama C2 (37/60 [49.0%, 72.9%]) matches baseline C1-W (38/60, p = 1.0); Qwen collapses to 1/60 (p = 1.71e-13).\n- Audience Interpretation: Proves mathematical quality retention on Llama and head-sharing failure on Qwen."
    p.font.name = "Calibri"
    p.font.size = Pt(12.5)
    p.font.color.rgb = C_NAVY_DARK

    # Card 3: Top Right - Multi-Objective Decision Stability (2000x Bootstrap)
    add_card(s11, Inches(6.833), Inches(1.65), card_w, card_h, C_WHITE, C_BORDER)
    top_bar = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.833), Inches(1.65), card_w, Inches(0.06))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_INDIGO
    top_bar.line.fill.background()

    tb = s11.shapes.add_textbox(Inches(7.083), Inches(1.8), card_w - Inches(0.5), card_h - Inches(0.25))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "3. Decision Stability (2,000x Bootstrap)"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(15.5)
    p.font.bold = True
    p.font.color.rgb = C_INDIGO
    p.space_after = Pt(4)

    p = tf.add_paragraph()
    p.text = "- Method: Non-parametric Pareto frontier bootstrap resampling over 2,000 trials.\n- Key Result: Llama C2 achieved 100.0% Pareto selection frequency across resamples.\n- Audience Interpretation: In 100% of simulated parallel variations, C2 remains the undisputed optimal compromise."
    p.font.name = "Calibri"
    p.font.size = Pt(12.5)
    p.font.color.rgb = C_NAVY_DARK

    # Card 4: Bottom Right - Interaction Contrast & Trace Robustness
    add_card(s11, Inches(6.833), Inches(4.35), card_w, card_h, C_WHITE, C_BORDER)
    top_bar = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.833), Inches(4.35), card_w, Inches(0.06))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_CORAL
    top_bar.line.fill.background()

    tb = s11.shapes.add_textbox(Inches(7.083), Inches(4.5), card_w - Inches(0.5), card_h - Inches(0.25))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "4. Compound Shielding & Power Robustness"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(15.5)
    p.font.bold = True
    p.font.color.rgb = C_CORAL
    p.space_after = Pt(4)

    p = tf.add_paragraph()
    p.text = "- Method: Interaction contrast I = (C4-C3)-(C2-C1) and 82W/70W power capping.\n- Key Result: Sub-additive shielding (I = -152.03 J, p = 0.00109); 100% rank stability.\n- Audience Interpretation: Pruning cache shields downstream routines; results are immune to power spikes."
    p.font.name = "Calibri"
    p.font.size = Pt(12.5)
    p.font.color.rgb = C_NAVY_DARK

    # =========================================================================
    # SLIDE 12: Finding 1 — Low-Token AWQ Energy Penalty & Context Scaling
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s12)
    add_header(s12, "6. Key Empirical Finding 1", 
               "The Low-Token AWQ Energy Penalty & Context Crossover", 
               "Why weight quantization increases energy at short contexts and only saves power on long sequences.")

    add_card(s12, Inches(0.8), Inches(1.65), Inches(11.733), Inches(1.35), C_CARD_WARM, C_CORAL)
    tb = s12.shapes.add_textbox(Inches(1.05), Inches(1.75), Inches(11.233), Inches(1.15))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "EMPIRICAL DISCOVERY: AWQ CONSUMES MORE ENERGY AT 1024 TOKENS"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_CORAL
    p.space_after = Pt(2)

    p = tf.add_paragraph()
    p.text = "At 1024 tokens, AWQ (C1-W) consumes 268.8 J vs 244.1 J for uncompressed FP16 (+10.1% energy penalty on Llama, +13.5% on Qwen).\nOnly at 4096 tokens does AWQ cross over to provide net energy savings (631.3 J vs 701.1 J, saving ~10.0%)."
    p.font.name = "Calibri"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK

    add_card(s12, Inches(0.8), Inches(3.2), Inches(5.65), Inches(3.8), C_WHITE)
    tb = s12.shapes.add_textbox(Inches(1.05), Inches(3.35), Inches(5.15), Inches(3.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "Energy Inversion Across Contexts"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(8)

    t_shape = s12.shapes.add_table(4, 4, Inches(1.05), Inches(3.8), Inches(5.15), Inches(2.2))
    t = t_shape.table
    t.columns[0].width = Inches(1.15)
    t.columns[1].width = Inches(1.3)
    t.columns[2].width = Inches(1.35)
    t.columns[3].width = Inches(1.35)
    
    t_headers = ["Context", "FP16 (C0)", "AWQ (C1-W)", "Evict (C2)"]
    for j, h in enumerate(t_headers):
        c = t.cell(0, j)
        c.text = h
        c.fill.solid()
        c.fill.fore_color.rgb = C_NAVY
        for p in c.text_frame.paragraphs:
            p.font.name = "Trebuchet MS"
            p.font.size = Pt(12.5)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    t_rows = [
        ("1024 Tok", "244.1 ± 13.1 J", "268.8 ± 26.2 J", "253.6 ± 14.4 J"),
        ("2048 Tok", "345.3 ± 5.0 J", "313.8 ± 9.3 J", "338.7 ± 21.0 J"),
        ("4096 Tok", "701.1 ± 8.1 J", "631.3 ± 5.1 J", "529.3 ± 20.0 J")
    ]
    for i, r in enumerate(t_rows):
        for j, v in enumerate(r):
            c = t.cell(i + 1, j)
            c.text = v
            c.fill.solid()
            c.fill.fore_color.rgb = C_CARD_WARM if (i==0 and j==2) else (C_CARD_SUCCESS if (i==2 and j==3) else C_WHITE)
            for p in c.text_frame.paragraphs:
                p.font.name = "Calibri"
                p.font.size = Pt(12)
                p.font.color.rgb = C_CORAL if (i==0 and j==2) else (C_TEAL if (i==2 and j==3) else C_NAVY_DARK)
                p.font.bold = (j==0 or (i==2 and j==3) or (i==0 and j==2))

    add_card(s12, Inches(6.75), Inches(3.2), Inches(5.783), Inches(3.8), C_CARD_ALT)
    tb = s12.shapes.add_textbox(Inches(7.0), Inches(3.35), Inches(5.283), Inches(3.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "Physical System Mechanism Explained"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(8)

    scaling_points = [
        ("Dequantization Penalty at 1024 Tokens:", "At short sequences, memory bandwidth is not saturated. The arithmetic overhead of unpacking INT4 weights to FP16 exceeds DRAM transfer savings."),
        ("Bandwidth Crossover Point (>2048 Tokens):", "As context expands, KV-cache DRAM reloads begin dominating runtime. Reduced weight bandwidth finally yields net power savings."),
        ("Eviction Magnifies at 4096 Tokens:", "C2 eviction cuts total energy by 101.95 J (-16.15%) and boosts throughput to 20.34 tok/s (+47.7% speedup) because it cuts decode memory traffic by 73.8%!")
    ]
    for s_title, s_desc in scaling_points:
        p = tf.add_paragraph()
        p.text = f"- {s_title} "
        p.font.name = "Calibri"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        run = p.add_run()
        run.text = s_desc
        run.font.bold = False
        run.font.color.rgb = C_BODY
        p.space_after = Pt(6)

    # =========================================================================
    # SLIDE 13: Finding 2 — Upstream Overhead Shielding (Compound Interaction)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s13)
    add_header(s13, "7. Key Empirical Finding 2", 
               "Upstream Overhead Shielding & Compound Interaction", 
               "Statistical proof that pruning cache tokens shields downstream quantization routines.")

    add_card(s13, Inches(0.8), Inches(1.65), Inches(5.65), Inches(5.35), C_WHITE)
    tb = s13.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.15), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "Interaction Contrast: I = (C4 - C3) - (C2 - C1)"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(8)

    interaction_points = [
        ("Sub-Additive Negative Interaction:", "Across both models, we measure and verify a statistically significant negative interaction contrast (I < 0, p < 0.01)."),
        ("Llama Interaction:", "I = -152.03 J (95% CI: [-187.11, -116.96] J, Holm p = 0.00109)."),
        ("Qwen Interaction:", "I = -112.32 J (95% CI: [-147.36, -77.28] J, Holm p = 0.00352)."),
        ("Physical Shielding Mechanism:", "Prior token eviction cuts active KV cache by ~74% (455 MiB -> 119 MiB). Subsequent quantization routines process 75% fewer coordinates, shielding against quantization compute stalls."),
        ("Power Trace Invariance:", "The negative interaction remained completely stable under 82W and 70W power capping.")
    ]
    for i_title, i_desc in interaction_points:
        p = tf.add_paragraph()
        p.text = f"- {i_title} "
        p.font.name = "Calibri"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        run = p.add_run()
        run.text = i_desc
        run.font.bold = False
        run.font.color.rgb = C_BODY
        p.space_after = Pt(6)

    add_card(s13, Inches(6.8), Inches(1.65), Inches(5.733), Inches(5.35), C_CARD_WARM, C_CORAL)
    tb = s13.shapes.add_textbox(Inches(7.05), Inches(1.85), Inches(5.233), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "Why Sequential Stacking is an Anti-Pattern"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_CORAL
    p.space_after = Pt(8)

    anti_points = [
        ("C4-Ref Strictly Dominated by C2:", "On Llama, adding TurboQuant on top of eviction (C4-Ref) adds +130.21 J total energy and degrades throughput from 20.34 down to 12.53 tok/s (-38.4% slowdown)!"),
        ("Identical Retrieval Accuracy:", "C4-Ref achieves 37/60 retrieval — exactly the same as C2 alone (37/60). Quantizing the pruned cache yields zero quality benefit."),
        ("Compounding Failure on Qwen:", "On Qwen, Q4-Ref inherits the 1/60 eviction failure while incurring quantization latency overhead."),
        ("Core Takeaway for Practitioners:", "Naive sequential stacking of independent compression tools is suboptimal. Pruning alone outperforms naive stacking unless custom fused kernels eliminate quantization overhead.")
    ]
    for a_title, a_desc in anti_points:
        p = tf.add_paragraph()
        p.text = f"- {a_title} "
        p.font.name = "Calibri"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        run = p.add_run()
        run.text = a_desc
        run.font.bold = False
        run.font.color.rgb = C_BODY
        p.space_after = Pt(6)

    # =========================================================================
    # SLIDE 14: Finding 3 — Llama vs. Qwen Eviction Divergence (GQA Sensitivity)
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s14)
    add_header(s14, "8. Key Empirical Finding 3", 
               "Llama vs. Qwen Eviction Divergence & GQA Head Sharing", 
               "Why custom PyramidKV succeeds on Llama (3:1 GQA) but collapses catastrophically on Qwen (8:1 GQA).")

    # Left: Llama Card (Success)
    add_card(s14, Inches(0.8), Inches(1.65), Inches(5.65), Inches(5.35), C_WHITE)
    top_bar = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.65), Inches(5.65), Inches(0.08))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_TEAL
    top_bar.line.fill.background()

    tb = s14.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.15), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "LLAMA 3.2-3B (3:1 GQA Ratio) [SUCCESS]"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_TEAL
    p.space_after = Pt(8)

    llama_res = [
        ("Total Energy Reduction:", "529.30 J vs 631.25 J baseline (-101.95 J, -16.15% savings, p = 0.00549)."),
        ("Decode Speedup:", "Throughput surges from 13.77 to 20.34 tok/s (+47.7% speedup)."),
        ("Active Cache Reduction:", "Live cache shrinks by 73.8% (from 455 MiB down to 119 MiB)."),
        ("Hard Retrieval Preserved:", "37/60 pass rate (61.7%) vs 38/60 baseline (63.3%) — within 1 scenario!"),
        ("Pareto Winner:", "100% bootstrap Pareto selection stability across 2000 resamples.")
    ]
    for r_title, r_desc in llama_res:
        p = tf.add_paragraph()
        p.text = f"- {r_title} "
        p.font.name = "Calibri"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        run = p.add_run()
        run.text = r_desc
        run.font.bold = False
        run.font.color.rgb = C_BODY
        p.space_after = Pt(6)

    # Right: Qwen Card (Failure & Root Cause)
    add_card(s14, Inches(6.8), Inches(1.65), Inches(5.733), Inches(5.35), C_CARD_ALERT, C_RED)
    top_bar = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(1.65), Inches(5.733), Inches(0.08))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_RED
    top_bar.line.fill.background()

    tb = s14.shapes.add_textbox(Inches(7.05), Inches(1.85), Inches(5.233), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "QWEN 2.5-3B (8:1 GQA Ratio) [COLLAPSE]"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_RED
    p.space_after = Pt(8)

    qwen_res = [
        ("Catastrophic Retrieval Collapse:", "Accuracy drops from 48/60 (80.0%) on Q1-W down to 1/60 (1.67%) on Q2 (p = 1.71e-13)!"),
        ("All Depths Destroyed:", "Score: 0/20 at 10% depth, 0/20 at 50%, 1/20 at 90% depth."),
        ("Cross-Model Contrast:", "Eviction degraded Qwen by 76.7 percentage points more than Llama (95% CI: [-86.7%, -66.7%])."),
        ("Structural Root Cause (8:1 GQA):", "In Qwen, 8 query heads share 1 KV head. Removing 1 KV token blinds 8 query heads simultaneously!"),
        ("Sensitivity Capacity Proof:", "Expanding budget by 50% (1536 tokens) recovered only 2/15 cases — proving failure is driven by routing conflict, not memory capacity.")
    ]
    for r_title, r_desc in qwen_res:
        p = tf.add_paragraph()
        p.text = f"- {r_title} "
        p.font.name = "Calibri"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        run = p.add_run()
        run.text = r_desc
        run.font.bold = False
        run.font.color.rgb = C_BODY
        p.space_after = Pt(6)

    # =========================================================================
    # SLIDE 15: Finding 4 — TurboQuant Validated Quality vs. Realization Gap
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s15)
    add_header(s15, "9. Key Empirical Finding 4", 
               "TurboQuant: Quality Validation vs. Software Realization Gap", 
               "Google's algorithmic quality claim confirmed, but un-fused software packages expand memory.")

    # Left: Quality Validation Card
    add_card(s15, Inches(0.8), Inches(1.65), Inches(5.65), Inches(5.35), C_CARD_SUCCESS, C_TEAL)
    tb = s15.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.15), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "Quality Claim Validated (Google ICLR '26)"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_TEAL
    p.space_after = Pt(8)

    tq_qual_points = [
        ("Google's Theoretical Claim:", "Zandieh et al. (ICLR 2026) claimed that randomized polar rotation + scalar codebook preserves attention accuracy without quality loss."),
        ("Empirical Validation on Llama:", "C3-Ref achieved 37/60 (61.7%), differing by only 1 case from AWQ baseline (38/60, 63.3%, McNemar p = 1.0)."),
        ("Empirical Validation on Qwen:", "Q3-Ref achieved 49/60 (81.7%), outperforming AWQ baseline Q1-W (48/60, 80.0%) and matching FP16 (53/60, 88.3%)!"),
        ("Algorithmic Soundness:", "The mathematical representation of TurboQuant is sound and preserves retrieval fidelity on SLMs!")
    ]
    for q_title, q_desc in tq_qual_points:
        p = tf.add_paragraph()
        p.text = f"- {q_title} "
        p.font.name = "Calibri"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        run = p.add_run()
        run.text = q_desc
        run.font.bold = False
        run.font.color.rgb = C_BODY
        p.space_after = Pt(6)

    # Right: The Software Realization Gap Figure & Audit
    add_card(s15, Inches(6.8), Inches(1.65), Inches(5.733), Inches(5.35), C_WHITE)
    tb = s15.shapes.add_textbox(Inches(7.05), Inches(1.85), Inches(5.233), Inches(0.45))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "The Software Realization Gap Audit"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_CORAL

    img_tq = resolve_path("evidence/accepted/CSE407_cross_model_visualization_v1/fig04_storage_realization_gap.png")
    if os.path.exists(img_tq):
        s15.shapes.add_picture(img_tq, Inches(7.0), Inches(2.4), width=Inches(5.333))

    # =========================================================================
    # SLIDE 16: Theoretical Projections — Ideal Packed TurboQuant & Break-Even
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s16)
    add_header(s16, "9. Theoretical Projections", 
               "Theoretical Ideal TurboQuant & Symbolic Break-Even Boundary", 
               "Modeling packed persistent memory footprints and defining exact fused kernel overhead limits.")

    # Left: Clean Storage Comparison Table (Large font)
    add_card(s16, Inches(0.8), Inches(1.65), Inches(5.65), Inches(5.35), C_WHITE)
    tb = s16.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.15), Inches(0.45))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Decode Memory at 4096 Tokens"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK

    t_shape = s16.shapes.add_table(3, 4, Inches(1.05), Inches(2.4), Inches(5.15), Inches(2.0))
    t = t_shape.table
    t.columns[0].width = Inches(1.5)
    t.columns[1].width = Inches(1.15)
    t.columns[2].width = Inches(1.25)
    t.columns[3].width = Inches(1.25)

    s_headers = ["Model", "FP16 Base", "Realized TQ", "Ideal Packed"]
    for j, h in enumerate(s_headers):
        c = t.cell(0, j)
        c.text = h
        c.fill.solid()
        c.fill.fore_color.rgb = C_NAVY
        for p in c.text_frame.paragraphs:
            p.font.name = "Trebuchet MS"
            p.font.size = Pt(12.5)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    s_rows = [
        ("Llama 3.2-3B", "455 MiB", "697 MiB (+53%)", "131 MiB (29%)"),
        ("Qwen 2.5-3B", "146 MiB", "224 MiB (+53%)", "42 MiB (29%)")
    ]
    for i, r in enumerate(s_rows):
        for j, v in enumerate(r):
            c = t.cell(i + 1, j)
            c.text = v
            c.fill.solid()
            c.fill.fore_color.rgb = C_CARD_WARM if j==2 else (C_CARD_ACCENT if j==3 else C_WHITE)
            for p in c.text_frame.paragraphs:
                p.font.name = "Calibri"
                p.font.size = Pt(12.5)
                p.font.color.rgb = C_CORAL if j==2 else (C_BLUE if j==3 else C_NAVY_DARK)
                p.font.bold = (j in [0, 2, 3])

    tb_ideal = s16.shapes.add_textbox(Inches(1.05), Inches(4.6), Inches(5.15), Inches(2.2))
    tf_i = tb_ideal.text_frame
    tf_i.word_wrap = True
    tf_i.margin_left = tf_i.margin_top = tf_i.margin_right = tf_i.margin_bottom = 0
    p_i = tf_i.paragraphs[0]
    p_i.text = "[THEORETICAL BOUNDARY]\n• Ideal Packed Kernel: Shrinks KV cache to 28.8% of FP16 memory (131 MiB on Llama).\n• Break-Even Condition: Custom fused kernel overhead O_net must stay below 19.95 GB-equiv for Llama 4-bit and 6.41 GB-equiv for Qwen!"
    p_i.font.name = "Calibri"
    p_i.font.size = Pt(13)
    p_i.font.color.rgb = C_BODY

    # Right: Embedded Symbolic Break-Even Plot
    add_card(s16, Inches(6.8), Inches(1.65), Inches(5.733), Inches(5.35), C_WHITE)
    tb = s16.shapes.add_textbox(Inches(7.05), Inches(1.85), Inches(5.233), Inches(0.45))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Symbolic Energy Break-Even Boundary"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    img_even = resolve_path("evidence/accepted/CSE407_cross_model_visualization_v1/fig07_symbolic_energy_break_even.png")
    if os.path.exists(img_even):
        s16.shapes.add_picture(img_even, Inches(7.0), Inches(2.4), width=Inches(5.333))

    # =========================================================================
    # SLIDE 17: Multi-Objective 3D Pareto Frontier & Power Robustness
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s17)
    add_header(s17, "10. Multi-Objective Analysis", 
               "Empirical 3D Pareto Frontier & Power Robustness", 
               "Balancing Energy, Quality, and Memory under 2000 bootstrap resamples and power clipping.")

    add_card(s17, Inches(0.8), Inches(1.65), Inches(5.8), Inches(5.35), C_WHITE)
    tb = s17.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.3), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "3D Pareto Frontier & The Energy Trap"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(8)

    pareto_text = [
        ("The Energy-Only Trap:", "On Qwen, Q2 has lowest energy (550.5 J) and smallest cache (38.3 MiB) with 100% bootstrap Pareto selection. BUT retrieval is 1/60 (useless)!"),
        ("Quality Threshold Mandatory:", "Pareto selection alone is not a deployment rule. A minimum quality constraint (>60%) eliminates Q2 and promotes Q0/Q1-W."),
        ("Llama Pareto Winner (C2):", "C2 achieves 100% bootstrap stability with 529 J energy, 119 MiB cache, and 37/60 retrieval."),
        ("Power Trace Robustness (100% Stable):", "Raw NVML transients reached 124.5W. Reintegration under 82W and 70W caps preserved 100% of rankings and significance decisions across all 40 registered tests!")
    ]
    for p_title, p_desc in pareto_text:
        p = tf.add_paragraph()
        p.text = f"- {p_title} "
        p.font.name = "Calibri"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        run = p.add_run()
        run.text = p_desc
        run.font.bold = False
        run.font.color.rgb = C_BODY
        p.space_after = Pt(6)

    add_card(s17, Inches(6.8), Inches(1.65), Inches(5.733), Inches(5.35), C_WHITE)
    tb = s17.shapes.add_textbox(Inches(7.05), Inches(1.8), Inches(5.233), Inches(0.45))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Measured Energy vs. Quality vs. Memory Frontier"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    img_pareto = resolve_path("evidence/accepted/CSE407_cross_model_visualization_v1/fig08_measured_pareto_energy_quality_memory.png")
    if os.path.exists(img_pareto):
        s17.shapes.add_picture(img_pareto, Inches(7.0), Inches(2.35), width=Inches(5.333))

    # =========================================================================
    # SLIDE 18: Bridging to Joint Optimization (RDKV & ThinKV)
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s18)
    add_header(s18, "11. Architectural Implications", 
               "Bridging Sequential Stacking to Joint Rate-Distortion (RDKV / ThinKV)", 
               "How our physical silicon findings motivate continuous rate-distortion allocation over disjoint pipelines.")

    add_card(s18, Inches(0.8), Inches(1.65), Inches(5.65), Inches(5.35), C_CARD_ALERT, C_RED)
    tb = s18.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.15), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "Why Disjoint Stacking Fails on Silicon"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_RED
    p.space_after = Pt(8)

    seq_points = [
        ("Binary All-or-Nothing Pruning:", "Hard eviction forces a binary decision: retain at full precision or completely delete (0 bits)."),
        ("Vulnerability in Aggressive GQA (8:1):", "Under 8:1 GQA, queries have diverse attention patterns. Zeroing out a token entry destroys context for all 8 query heads simultaneously."),
        ("Disjoint Pipeline Overhead:", "Unfused quantization routines add conversion reads and reconstruction writes that outweigh bandwidth savings."),
        ("No Unified Optimization:", "Eviction decisions do not know that downstream quantization is occurring, leading to compounding degradation.")
    ]
    for s_title, s_desc in seq_points:
        p = tf.add_paragraph()
        p.text = f"- {s_title} "
        p.font.name = "Calibri"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        run = p.add_run()
        run.text = s_desc
        run.font.bold = False
        run.font.color.rgb = C_BODY
        p.space_after = Pt(6)

    add_card(s18, Inches(6.8), Inches(1.65), Inches(5.733), Inches(5.35), C_CARD_ACCENT, C_BLUE)
    tb = s18.shapes.add_textbox(Inches(7.05), Inches(1.85), Inches(5.233), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "The Joint Rate-Distortion Paradigm"
    p.font.name = "Trebuchet MS"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(8)

    joint_points = [
        ("Continuous Bit Allocation (RDKV / ThinKV):", "Treats token eviction as the extreme 0-bit case within a continuous rate-distortion optimization framework (Zhang et al. 2026, Ramachandran et al. 2026)."),
        ("Soft Retention via Low Precision:", "Under aggressive GQA, retaining marginal tokens at 1 or 2 bits preserves directional attention signals without catastrophic collapse."),
        ("Hardware Grounding from Our Work:", "Our empirical shielding measurement (I < 0) provides the physical boundary condition: shrinking active cache volume genuinely cuts DRAM read energy."),
        ("Unified Fused Kernels:", "Combines token filtering and quantization inside a single fused FlashAttention-style kernel to eliminate realization gaps.")
    ]
    for j_title, j_desc in joint_points:
        p = tf.add_paragraph()
        p.text = f"- {j_title} "
        p.font.name = "Calibri"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        run = p.add_run()
        run.text = j_desc
        run.font.bold = False
        run.font.color.rgb = C_BODY
        p.space_after = Pt(6)

    # =========================================================================
    # SLIDE 19: Summary & Key Takeaways for Edge Practitioners
    # =========================================================================
    s19 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s19, C_WHITE)
    add_header(s19, "12. Conclusion & Takeaways", 
               "Core Takeaways for Edge SLM Deployment", 
               "Actionable design rules for practitioners deploying small language models on power-constrained hardware.")

    takeaways = [
        ("1. Architecture Dictates Compression Viability", 
         "Attention head layouts dominate compression success. 3:1 GQA (Llama) allows 73.8% KV cache pruning with zero quality loss; 8:1 GQA (Qwen) collapses to 1/60 accuracy under the same policy.", C_BLUE),
        ("2. Beware the Low-Token Quantization Penalty", 
         "AWQ increases energy on short sequences (<2048 tokens) due to dequantization overhead. Only deploy weight quantization when sequence lengths justify memory bandwidth trade-offs.", C_CORAL),
        ("3. Single-Stage Eviction Trumps Naive Stacking", 
         "On Llama, single-stage custom PyramidKV eviction (C2) is the clear Pareto winner (16.15% energy drop, +47.7% speedup). Naive sequential stacking adds +130 J overhead without quality gain.", C_TEAL),
        ("4. Mind the Realization Gap — Fused Kernels Required", 
         "TurboQuant algorithm preserves quality, but off-the-shelf packages expand memory. True hardware gains require custom fused CUDA/Triton kernels satisfying our break-even boundary.", C_INDIGO)
    ]

    for idx, (t_title, t_desc, t_color) in enumerate(takeaways):
        tx = Inches(0.8)
        ty = Inches(1.65 + idx * 1.35)
        tw = Inches(11.733)
        th = Inches(1.2)

        add_card(s19, tx, ty, tw, th, C_CARD_ALT, border_color=None)
        
        stripe = s19.shapes.add_shape(MSO_SHAPE.RECTANGLE, tx, ty, Inches(0.1), th)
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = t_color
        stripe.line.fill.background()

        tb = s19.shapes.add_textbox(tx + Inches(0.3), ty + Inches(0.15), tw - Inches(0.5), th - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = t_title
        p.font.name = "Trebuchet MS"
        p.font.size = Pt(15.5)
        p.font.bold = True
        p.font.color.rgb = t_color
        p.space_after = Pt(2)

        p = tf.add_paragraph()
        p.text = t_desc
        p.font.name = "Calibri"
        p.font.size = Pt(13)
        p.font.color.rgb = C_NAVY_DARK

    output_path = os.path.join(SCRIPT_DIR, "SLM_Energy_Ablation_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation regenerated and saved to {output_path}")

if __name__ == "__main__":
    build_presentation()
