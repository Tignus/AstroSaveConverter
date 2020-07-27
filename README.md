
# Table of contents
- [Table of contents](https://github.com/Tignus/AstroSaveConverter#table-of-contents)
- [AstroSaveConverter](https://github.com/Tignus/AstroSaveConverter#astrosaveconverter)
- [Convert your game saves](https://github.com/Tignus/AstroSaveConverter#convert-your-game-saves)
	- [XBOX to Steam](https://github.com/Tignus/AstroSaveConverter#xbox-to-steam)
	- [Steam to XBOX](https://github.com/Tignus/AstroSaveConverter#steam-to-xbox)
	- [How to use](https://github.com/Tignus/AstroSaveConverter#how-to-use)
- [FAQ](https://github.com/Tignus/AstroSaveConverter#faq)
- [Contributing](https://github.com/Tignus/AstroSaveConverter#contributing)
- [Special thanks](https://github.com/Tignus/AstroSaveConverter#special-thanks) 
# AstroSaveConverter

/!\ PLEASE ONLY USE THIS TOOL ON COPIES OF YOUR SAVE FILES. USE AT YOUR OWN RISK /!\
This tool is in alpha release and is still being developped. We aren't confident il will work in any case, please give us your feedback !

# Convert your game saves

This project aims to help Astroneer players switching from Microsoft XBOX save format to Steam save format.
Astroneer can be played either on Steam or on XBOX Gamepass and both have different ways to store save files. Steam games are saved in one file, no matter the size of the save, while XBOX won't go over 16MB files, splitting the saves into several chunks if they get too big.

## XBOX to Steam

The tool is meant to convert XBOX save files into Steam save files. In order to do so, it reads the "container" file that states how XBOX saves are divided (name and number of chunks that compose each saves). It will then assemble those chunks into one file that can be used by Steam or dedicated servers.

## Steam to XBOX

It is currently not possible to convert a Steam save into XBOX save

## How to use

 - Please only use this tool with **copies** of your game saves.
 - XBOX saves can be found here :
`C:\Users\%username%\AppData\Local\Packages\SystemEraSoftworks.29415440E1269_ftk5pbg2rayv2\SystemAppData\wgs\{list of random characters}\`
 - Steam saves can be found here :
    `C:\Users\%Username%\AppData\Local\Astro\Saved\SaveGames`
    
 - Once you copied the files in a new folder, start AstroSaveConverter.exe in the same folder.
 - The tool will automatically detect the container files and ask you to chose one.
 - It will then ask you to choose wich save(s) you want to convert. Select one or several.
 - You will be able to rename the save. Saves can only contain alphanumeric characters and must be less than 30 characters long.
 - if the save already exists, you will be able to rename or overwrite the existing file.
 - Congratulations, you're done ! AstroSaveConverter will now generate your new save file.

# FAQ
- **I really don't understand "save files", "chunk"...***
Let us recap for you :
*Save* : Astroneer save file, XBOX or Steam.
*Chunk* : part of an Astroneer save if the total save exceeds 16MB. Each chunk size is max 16MB. And XBOX save can be composed of one or several chunks.
*Container* : file that tells the game which files constitute which save. Only for XBOX.

 - ***The text is too small, I can't read anything !***
 We are not able to change the font size for you. Right click on the **title bar** and select **Proprieties**. Navigate to the **Font** tab and change the font size of your command prompt.

- ***Why can't I use more than 30 characters to rename my save ?***
We found out that even though Astroneer allows more than 30 characters, it can cause errors when the save become bigger and is splitted in a second chunk : the chunk name in the container file will now indicate the part number which adds extra characters. Creative games also have an extra character.

- ***Why can I only use alphanumeric characters in my save names ?***
We didn't know which special characters were allowed in Astroneer and it would be too long to test every option. To avoid compatibility errors, we chose to restrict which characters can be used. You can however edit the save name directly in Astroneer

- ***How can I know what will be added in the tool ?***
Please feel free to look at [our Trello](https://trello.com/b/jM8tx7GU/astro-save-converter) (in French)

# Contributing
Contributions are greatly appreciated. Do not hesitate to fork the project and open pull requests !

# Special thanks

We (Tignus and EmptyProfile) would like to thanks everyone who helped us in the process of developping our tool:

- Ricky Davis and his too [AstroLauncher](https://github.com/ricky-davis/AstroLauncher) which we used to start building our own AstroSaveConverter
- Gina and Cyber for their contribution to the "[Importing and Converting files between Microsoft & Microsoft OR Microsoft & Steam](https://forum.systemera.net/topic/53054-importing-and-converting-files-between-microsoft-microsoft-or-microsoft-steam/)" thread
- The [Twich](http://twitch.tv/tignus) chat and in particular WinXaito, AbsoluteVirtue, Zic0h for their help and support during the long hours of (improductive) coding
