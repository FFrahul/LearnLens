"""LearnLens AI visual theme."""

GLOBAL_CSS = """
<style>
:root {
    --ll-indigo: #4F46E5;
    --ll-indigo-dark: #3730A3;
    --ll-teal: #0F766E;
    --ll-teal-light: #CCFBF1;
    --ll-navy: #172554;
    --ll-muted: #64748B;
    --ll-line: #DDE5F0;
    --ll-bg: #F8FAFC;
    --ll-white: #FFFFFF;
    --ll-success: #166534;
    --ll-warning: #92400E;
    --ll-error: #991B1B;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1180px;
    padding-top: 1.25rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4 {
    letter-spacing: -0.01em;
}

.ll-hero {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 12px;
    padding: 14px 18px;
    border: 1px solid #3730A3;
    border-radius: 12px;
    background: linear-gradient(135deg, #172554 0%, #312E81 100%);
    color: #FFFFFF;
}

.ll-hero-title {
    font-size: 1.35rem;
    font-weight: 800;
    line-height: 1.2;
}

.ll-hero-copy {
    margin-top: 4px;
    color: #CBD5E1;
    font-size: 0.92rem;
}

.ll-hero-chips {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 6px;
}

.ll-chip {
    display: inline-flex;
    align-items: center;
    min-height: 28px;
    padding: 4px 10px;
    border: 1px solid rgba(255, 255, 255, 0.22);
    border-radius: 999px;
    color: #E0E7FF;
    background: rgba(255, 255, 255, 0.08);
    font-size: 0.78rem;
    font-weight: 700;
}

.ll-stepper {
    position: sticky;
    top: 0;
    z-index: 100;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 8px;
    margin: 8px 0 16px;
    padding: 8px;
    border: 1px solid var(--ll-line);
    border-radius: 12px;
    background: rgba(248, 250, 252, 0.96);
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
}

.ll-step {
    min-height: 64px;
    padding: 10px 12px;
    border: 1px solid var(--ll-line);
    border-radius: 10px;
    background: var(--ll-white);
    color: var(--ll-navy);
}

.ll-step.active {
    border-color: var(--ll-indigo);
    box-shadow: inset 0 3px 0 var(--ll-indigo);
}

.ll-step.done {
    border-color: #99D8CF;
    background: #F0FDFA;
}

.ll-step.locked {
    color: #94A3B8;
    background: #F1F5F9;
}

.ll-step-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    margin-right: 8px;
    border-radius: 50%;
    background: #EEF2FF;
    color: var(--ll-indigo-dark);
    font-weight: 800;
}

.ll-step.done .ll-step-number {
    background: var(--ll-teal);
    color: #FFFFFF;
}

.ll-step.locked .ll-step-number {
    background: #E2E8F0;
    color: #64748B;
}

.ll-step-name {
    font-weight: 800;
}

.ll-step-hint {
    margin-top: 4px;
    font-size: 0.78rem;
    color: var(--ll-muted);
}

.ll-card {
    margin: 8px 0;
    padding: 16px;
    border: 1px solid var(--ll-line);
    border-radius: 12px;
    background: var(--ll-white);
    box-shadow: 0 5px 16px rgba(15, 23, 42, 0.05);
}

.ll-card.info {
    border-left: 4px solid var(--ll-indigo);
}

.ll-card.success {
    border-left: 4px solid var(--ll-success);
}

.ll-card.warning {
    border-left: 4px solid var(--ll-warning);
    background: #FFFBEB;
}

.ll-card.error {
    border-left: 4px solid var(--ll-error);
    background: #FEF2F2;
}

.ll-empty {
    max-width: 620px;
    margin: 24px auto;
    padding: 24px;
    text-align: center;
}

.ll-empty-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--ll-navy);
}

.ll-empty-copy {
    margin: 6px 0 14px;
    color: var(--ll-muted);
}

.ll-status-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.ll-status-chip {
    display: inline-flex;
    align-items: center;
    min-height: 28px;
    padding: 4px 9px;
    border: 1px solid var(--ll-line);
    border-radius: 999px;
    background: #FFFFFF;
    color: #334155;
    font-size: 0.76rem;
    font-weight: 700;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px;
    padding: 4px;
    overflow-x: auto;
    border: 1px solid var(--ll-line);
    border-radius: 10px;
    background: #F1F5F9;
}

[data-testid="stTabs"] button[role="tab"] {
    min-height: 42px;
    padding: 8px 12px;
    border-radius: 8px;
    white-space: nowrap;
}

[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: #FFFFFF;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.10);
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none;
}

.stButton > button {
    border-radius: 8px;
    font-weight: 700;
}

.stButton > button[kind="primary"] {
    border: none;
    background: var(--ll-indigo);
}

[data-testid="stFileUploaderDropzone"] {
    border-radius: 12px;
    border: 1.5px dashed #A5B4FC;
    background: #EEF2FF;
}

[data-testid="stMetric"] {
    padding: 8px 10px;
    border: 1px solid var(--ll-line);
    border-radius: 10px;
    background: #FFFFFF;
}

[data-testid="stSidebar"] {
    border-right: 1px solid var(--ll-line);
}

@media (max-width: 700px) {
    .ll-hero {
        align-items: flex-start;
        flex-direction: column;
    }
    .ll-hero-chips {
        justify-content: flex-start;
    }
    .ll-stepper {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
</style>
"""
