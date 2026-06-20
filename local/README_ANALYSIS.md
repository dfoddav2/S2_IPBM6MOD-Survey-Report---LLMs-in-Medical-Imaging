# Medical Image Analysis with MLLMs

This project analyzes medical images from NEJM Image Challenge using Multimodal Large Language Models (MLLMs) via oMLX.

## Setup

1. Ensure oMLX is running on your system:
   ```bash
   # Start oMLX server (adjust command based on your installation)
   omlx serve
   ```

2. Install dependencies using UV:
   ```bash
   cd local
   uv venv
   uv pip install -r requirements.txt
   ```

3. Verify oMLX is accessible:
   ```bash
   curl http://127.0.0.1:8000/health
   ```

## Usage

Run the analysis script:
```bash
cd local
uv run analyze_medical_images.py
```

The script performs two tests:
1. **Test 1**: Analyze image with question only
2. **Test 2**: Analyze image with question + multiple choice options

## Configuration

Edit `local/analyze_medical_images.py` to:
- Change `OMLX_URL` if oMLX runs on different port
- Modify `OMLX_MODEL` parameter to use different MLLM
- Update image paths to analyze different images

## API Key

If oMLX requires authentication, set the API key as an environment variable:

```bash
export OMLX_API_KEY="your-api-key-here"
cd local
uv run analyze_medical_images.py
```

**Note:** If you're using a different shell or want the variable to persist across terminal sessions, add the export command to your shell configuration file (e.g., `~/.zshrc` or `~/.bashrc`).

## Expected Output

The script will show:
- Model's diagnosis for NEJM case
- Comparison with expected answer (Pulmonary mucormycosis)
- Success rate comparison with human participants (51%)

### Example run with Qwen 3.6 35B-A3B

```text
============================================================
NEJM Image Challenge Analysis
============================================================

Using endpoint: http://127.0.0.1:8000/v1/chat/completions
Using model: Qwen3.6-35B-A3B-Claude-4.7-Opus-Reasoning-Distilled-MLX-oQ4-MTP

Found 3 case(s): ['nejm-02-05-26', 'nejm-03-19-26', 'nejm-06-04-26']

############################################################
# CASE 1/3: nejm-02-05-26
############################################################
Description: A 49-year-old man with acute myeloid leukemia who had been admitted to the hospital for induction chemotherapy was evalu...
Expected answer: Pulmonary mucormycosis (human success: 51%)

[TEST 1] nejm-02-05-26 - Analyzing WITHOUT options...
Response: Invasive pulmonary aspergillosis

[TEST 2] nejm-02-05-26 - Analyzing WITH options...
Response: Pulmonary mucormycosis

############################################################
# CASE 2/3: nejm-03-19-26
############################################################
Description: A 65-year-old woman with a recent history of acute necrotizing pancreatitis presented with a 5-day history of abdominal ...
Expected answer: Walled-off pancreatic necrosis (human success: 55%)

[TEST 1] nejm-03-19-26 - Analyzing WITHOUT options...
Response: Infected pancreatic necrosis (likely with gas formation/abscess)

[TEST 2] nejm-03-19-26 - Analyzing WITH options...
Response: Walled-off pancreatic necrosis

############################################################
# CASE 3/3: nejm-06-04-26
############################################################
Description: An 11-year-old girl presented to the orthopedic clinic with a 1-month history of right thigh pain that worsened at night...
Expected answer: Osteosarcoma (human success: 59%)

[TEST 1] nejm-06-04-26 - Analyzing WITHOUT options...
Response: Osteosarcoma

[TEST 2] nejm-06-04-26 - Analyzing WITH options...
Response: Osteosarcoma

============================================================
SUMMARY
============================================================

nejm-02-05-26
  Expected:      Pulmonary mucormycosis
  No options:    Invasive pulmonary aspergillosis
  With options:  Pulmonary mucormycosis

nejm-03-19-26
  Expected:      Walled-off pancreatic necrosis
  No options:    Infected pancreatic necrosis (likely with gas formation/abscess)
  With options:  Walled-off pancreatic necrosis

nejm-06-04-26
  Expected:      Osteosarcoma
  No options:    Osteosarcoma
  With options:  Osteosarcoma
```

## Notes

- Ensure images are in JPEG format
- oMLX server must be running before executing the script
- Adjust timeout if model takes longer to respond