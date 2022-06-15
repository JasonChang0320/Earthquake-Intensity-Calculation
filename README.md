# Taiwan-Earthquake-Intensity-Calculation
  According to CWB new earthqauke intensity workflow, we use Hualian earthquake on Frebruary 2018 as an example to calulate earthquake record PGA (peak ground acceleration) (gal) and PGV (peak ground velocity) to classify to intensity. The workflow shows below.
  
  ![image](https://github.com/JasonChang0320/Taiwan-Earthquake-Intensity-Calculation/blob/main/markdown%20image/CWB%20earthquake%20intensity.jpg)
  
## file description
  **CWB_intensity_cal.py** is the main code that caculate intensity, and the input are earthquake 3 component waveforms.
  
  **error_filename.xlsx** recorded the broken waveform downloaded from CWB.
  
  **intensity_result** recorded each stations intensity,PGA and PGV.
  
  **plot&statistic.py** is to visualize the intensity result on Taiwan map and anlysis.
  
  **Fig** folder is some figure output from **plot&statistic.py**
  
  ## Result Map
    ![image]([https://github.com/JasonChang0320/Taiwan-Earthquake-Intensity-Calculation/blob/main/Fig/intensity.png](https://github.com/JasonChang0320/Taiwan-Earthquake-Intensity-Calculation/blob/main/Fig/intensity.png))
  
