# 🛡️   CONSCIA
**Building an Ethical and Responsible Tech Environment**

---

## 📌 Overview
CONSCIA is a **multi-module cybersecurity & monitoring suite** designed for the hackathon theme:  
**“Governing AI – Building Ethical and Responsible Tech Environment.”**

This toolkit focuses on **security, transparency, and ethical AI governance** by offering tools that:  
- Detect hidden data manipulation in AI inputs.  
- Monitor file & process integrity.  
- Secure sensitive data and credentials.  
- Audit network activity to prevent misuse.  
- Provide red-team simulations for resilience testing.  

Together, these modules promote **trustworthy AI adoption** by ensuring AI systems are protected from tampering, unauthorized access, and hidden malicious instructions.

---

## ⚙️ Features & Modules

| Module | File | Purpose |
|--------|------|---------|
| **File Integrity Monitor** | `filewatch.py`, `filewatch_db.json` | Tracks changes in critical files & datasets to prevent tampering. |
| **Steganography Detector** | `stegsniff.py` | Detects hidden malicious payloads in AI training/testing images. |
| **Process Monitor** | `procpeek.py` | Identifies suspicious processes that may steal or spy on AI models. |
| **Port & Network Scanner** | `pyporter.py` | Monitors unauthorized network activity to prevent data leaks. |
| **Password Auditing Tools** | `john4py.py`, `WPass_Recon.py` | Highlights weak credentials & prevents brute-force misuse of AI systems. |
| **Subdomain Enumerator** | `SubEnum.py` | Maps AI deployment surfaces to identify vulnerabilities. |
| **Activity Logger** | `k_log.pyw` | Maintains transparency logs for AI system activity. |

---

## 🏗️ Installation

Clone the repository:
```bash
git clone https://github.com/Muthukumaran-Official/Conscia.git
cd Conscia
