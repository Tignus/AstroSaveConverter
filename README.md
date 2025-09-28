


<br />
<p align="center">
  <img src="https://raw.githubusercontent.com/Tignus/AstroSaveConverter/master/assets/astroconverterlogo.ico" width="128px">
  <h3 align="center">AstroSaveConverter - Switch from XBOX to Steam</h3>

  <p align="center">
    <a href="https://github.com/Tignus/AstroSaveConverter/releases/latest">Latest release</a>
    ·
    <a href="https://github.com/Tignus/AstroSaveConverter/issues">Post an issue</a>
  </p>
</p>


# Table of contents
- [Table of contents](https://github.com/Tignus/AstroSaveConverter#table-of-contents)
- [AstroSaveConverter](https://github.com/Tignus/AstroSaveConverter#astrosaveconverter)
- [Convert your game saves](https://github.com/Tignus/AstroSaveConverter#convert-your-game-saves)
	- [Microsoft XBOX to Steam](https://github.com/Tignus/AstroSaveConverter#microsoft-xbox-to-steam)
	- [Steam to Microsoft XBOX](https://github.com/Tignus/AstroSaveConverter#steam-to-microsoft-xbox)
	- [How to use](https://github.com/Tignus/AstroSaveConverter#how-to-use)
- [Manual rollback procedure](https://github.com/Tignus/AstroSaveConverter#manual-rollback-procedure)
	- [Steam saves](https://github.com/Tignus/AstroSaveConverter#steam-saves)
	- [Microsoft XBOX saves](https://github.com/Tignus/AstroSaveConverter#microsoft-xbox-saves)
- [FAQ](https://github.com/Tignus/AstroSaveConverter#faq)
- [Contributing](https://github.com/Tignus/AstroSaveConverter#contributing)
- [Special thanks](https://github.com/Tignus/AstroSaveConverter#special-thanks) 
# AstroSaveConverter

/!\ PLEASE ONLY USE THIS TOOL ON COPIES OF YOUR SAVE FILES. USE AT YOUR OWN RISK /!\\

We aren't confident it will work in every case, please give us your feedback !

Be warned : content of your backpack may disappear. Please make sure you empty it before saving your game.

We can't afford to authenticate our software with a licence (waaaay too expensive) so you will have a Windows prompt if you try to run the .exe file. No worries, it's safe !
You must click on "more info" in order to be able to run the software

<br />
<p align="center">
	<img src="https://i.imgur.com/ZB7sROM.png" width="450px">
	<img src="https://i.imgur.com/43J4E5R.png" width="450px">
</p>
  

# Convert your game saves

This project aims to help Astroneer players switching from *Microsoft XBOX* save format to *Steam* save format.
Astroneer can be played either on *Steam* or on *XBOX* Gamepass and both have different ways to store save files. *Steam* games are saved in one file, no matter the size of the save, while XBOX won't go over 16MB files, splitting the saves into several chunks if they get too big.

## Microsoft XBOX to Steam

The tool is meant to convert *Microsoft XBOX* save files into Steam save files. In order to do so, it reads the "container" file that states how *Microsoft XBOX* saves are divided (name and number of chunks that compose each saves). It will then assemble those chunks into one file that can be used by Steam or dedicated servers.

## Steam to Microsoft XBOX

AstroSaveConverter now allows you to convert your *Steam* saves into *Microsoft XBOX* format !

## How to use

 - Please only use this tool with **copies** of your game saves.
 - XBOX saves can be found by pressing the **Windows key** + **R** and pasting this :

```cmd /c Powershell.exe "explorer ((Get-ChildItem $env:LOCALAPPDATA\Packages\SystemEraSoftworks*\SystemAppData\wgs\ -Recurse -Filter container.*).FullName | Where-Object { ((gc $_) -replace \"`0\",\"\") -match '\$(\d){4}'} | Split-Path)"```<br />

 Steam saves can be found here :
    `%LocalAppData%\Astro\Saved\SaveGames`
 - Copy all the files in a new folder on your desktop. Place AstroSaveConverter.exe in that new folder and run it.
 - The tool will automatically detect the container file(s) and ask you to chose one.
 - It will then ask you to choose wich save(s) you want to convert. Select one or several.
 - You will be able to rename the save. Saves can only contain alphanumeric characters and must be less than 30 characters long.
 - If the save already exists, you will be able to rename or overwrite the existing file.
 - Congratulations, you're done ! AstroSaveConverter will now generate your new save file.
	 - In a dedicated *Steam* save folder in case you converted from *Microsoft XBOX* to *Steam*
	 - Directly in your game folder if you converted from *Steam* to *Microsoft XBOX*. All you have to do is to launch your game

# Manual rollback procedure
If your save files have disappeared or have been corrupted, here's how to put the old ones back.
**Please always make sure to create a copy of your game save folder before using AstroSaveConverter even though we automatically create one for you**

## Steam saves
1. Make sure to close any running Astroneer program
2.  Go to your *Steam* save directory by pressing the **Windows
    key** + **R** and pasting this :    `%LocalAppData%\Astro\Saved\SaveGames`
3. Copy the backed up *Steam* save files into this folder

## Microsoft XBOX saves
 1. Make sure to close any running Astroneer program
 2. Wait for 1 minute for the game to update its save folder
 3. Open your *Microsoft XBOX* game save directory by pressing the **Windows
    key** + **R** and pasting this :

```cmd /c Powershell.exe "explorer ((Get-ChildItem $env:LOCALAPPDATA\Packages\SystemEraSoftworks*\SystemAppData\wgs\ -Recurse -Filter container.*).FullName | Where-Object { ((gc $_) -replace \"`0\",\"\") -match '\$(\d){4}'} | Split-Path)"```<br />

 4. Locate a file called **container.*** (the asterisk can be any number)
 5. Open the folder where you have made a copy of your original save files and edit the **container.*** file so the number matches the one seen in the *Microsoft XBOX* folder
 6. Delete all the content of the *Microsoft XBOX* save folder
 7. Copy all the save files and the updated **contaire.*** in the *Microsoft XBOX* save folder

# FAQ
- **I really don't understand "save files", "chunk"...*** <br />
Let us recap for you :<br />
*Save* : Astroneer save file, XBOX or Steam.<br />
*Chunk* : part of a XBOX Astroneer save if the total save exceeds 16MB. Each chunk size is max 16MB.<br />
*Container* : file that tells the game which chunks constitute which save. Only for XBOX.<br />

 - ***The text is too small, I can't read anything !*** <br />
 We are not able to change the font size for you. Right click on the **title bar** and select **Properties**. Navigate to the **Font** tab and change the font size of your command prompt.

- ***Why can't I use more than 30 characters to rename my save ?*** <br />
We found out that even though Astroneer allows more than 30 characters, it can cause errors when the save become bigger and is splitted in a second chunk : the chunk in the container file will now indicate the part number which adds extra characters. Creative games also have an extra character.

- ***Why can I only use alphanumeric characters in my save names ?*** <br />
We didn't know which special characters were allowed in Astroneer and it would be too long to test every option. To avoid compatibility errors, we chose to restrict which characters can be used. You can however edit the save name directly in Astroneer

- ***I did something wrong, how do I rollback ?*** <br />
You can read the rollback procedure [right on top](https://github.com/Tignus/AstroSaveConverter#manual-rollback-procedure) of this FAQ !

- ***How can I know which feature(s) will be added in the tool ?*** <br />
Please feel free to look at [our TODO list !](https://github.com/Tignus/AstroSaveConverter/projects/1)

# Contributing
Contributions are greatly appreciated. Do not hesitate to fork the project and open pull requests !
This software is distributed under the [GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/) license

## Documentation

To build the project documentation locally:

```bash
pip install -r requirements.txt
sphinx-build -b html docs/ build/html
```

# Special thanks

We (Tignus and EmptyProfile) would like to thanks everyone who helped us in the process of developping our tool:

- Ricky Davis and his [AstroLauncher](https://github.com/ricky-davis/AstroLauncher) which we used to start building our own AstroSaveConverter
- Gina and Cyber for their contribution to the "[Importing and Converting files between Microsoft & Microsoft OR Microsoft & Steam](https://forum.systemera.net/topic/53054-importing-and-converting-files-between-microsoft-microsoft-or-microsoft-steam/)" thread
- The Twitch chat and in particular WinXaito, AbsoluteVirtue, Zic0h, SyndGame, SamirJap, Elfou for their help and support during the long hours of (improductive) coding
