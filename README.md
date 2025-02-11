# Interview Grading Software

This Software is Made to Analyse candidate's video Resume, during Submission, this software uses various OpenCV Models, for Detectition of Physical Parameters like Posture, Smile, Eye Contact, and Energetic Start


Follow the Guide Along in order to Run the Software



This guide provides steps to set up a Python environment using `venv` and install dependencies.

## Prerequisites
- Ensure Python is installed (recommended version: 3.8 or later).
- Verify Python installation:
  ```sh
  python --version
  ```
  or
  ```sh
  python3 --version
  ```

## Creating a Virtual Environment
1. Navigate to your project directory:
   ```sh
   cd /path/to/your/project
   ```

2. Create a virtual environment:
   ```sh
   python -m venv venv
   ```
   or (for Linux/macOS users)
   ```sh
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   - **Windows**:
     ```sh
     venv\Scripts\activate
     ```
   - **Linux/macOS**:
     ```sh
     source venv/bin/activate
     ``` 

## Clone the Repository into your Project Directory 
  ```sh
  git clone  
  ``` 
## Go into the Project Directory 
```sh 
cd Video_Analysis
```

## Installing Dependencies
- Install required packages from `requirements.txt`:
  ```sh
  pip install -r requirements.txt 
  ``` 

## Run the Streamlit App 
```sh 
streamlit run Interview_Grader.py
```

After Opening the Streamlit Window you will see options to Upload the Video, upload your video in any format, wait for it to complete the processing, withing 10~20 secs you will get your PDF Report and you can Download it 

## Team 
1. Dhruv Gupta 
2. Samanway 
3. Ayush Mishra 
4. Deepesh Jha 
5. Anubhuti Anand 