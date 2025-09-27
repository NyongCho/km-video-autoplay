# km-video-autoplay
An automation tool that plays videos on km automatically.

## Overview
Automation script that logs into km, enters the classroom, navigates to a target chapter, and plays videos automatically.  
It waits for the remaining video time plus an extra 30 seconds, then proceeds to the next video.

## Environment
- OS: Windows 11
- Python: 3.11.0
- Selenium: 4.35.0
- Browser: Chrome (tested on latest version)

## Configuration
Before running, create a `config.json` file in the project root:
```json
{
    "user": {
        "id": "user@gmail.com",
        "pw": "Mypassword@123"
    },
    "video": {
        "class_url": "https://km.com/course/view.php?id=1234",
        "chapter": 4,
        "video_limit": 10
    }
}
```
- username : login ID
- password : login password
- classroom_url : classroom URL
- chapter : target chapter number
- video_limit : number of videos to scan and play


## How to Run
```
# install dependencies
pip install selenium==4.35.0

# run the program
python run.py
```


## Notes
- Tested only on Windows 11 with Chrome + matching ChromeDriver
- If km changes layout (XPath, DOM structure), the script may need updates.
- This tool is for educational and personal automation purposes.
