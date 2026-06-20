# Medical Image Analysis with MLLMs

This project analyzes medical images from NEJM Image Challenge using Multimodal Large Language Models (MLLMs) via oMLX.

## Setup

1. Ensure oMLX is running on your system:
   ```bash
   # Start oMLX server (adjust command based on your installation)
   omlx serve
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify oMLX is accessible:
   ```bash
   curl http://localhost:8080
   ```

## Usage

Run the analysis script:
```bash
python analyze_medical_images.py
```

The script performs two tests:
1. **Test 1**: Analyze image with question only
2. **Test 2**: Analyze image with question + multiple choice options

## Configuration

Edit the script to:
- Change `omlx_url` if oMLX runs on different port
- Modify `model` parameter to use different MLLM
- Update `image_path` to analyze different images

## Expected Output

The script will show:
- Model's diagnosis for NEJM case
- Comparison with expected answer (Pulmonary mucormycosis)
- Success rate comparison with human participants (51%)

## Notes

- Ensure images are in JPEG format
- oMLX server must be running before executing the script
- Adjust timeout if model takes longer to respond