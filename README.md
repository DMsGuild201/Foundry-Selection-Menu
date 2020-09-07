Hello! This python script has developed by [@dlivitz](https://github.com/dlivitz) and propagated by [@MrVauxs](https://github.com/MrVauxs).
### Basic Instructions

While on further updates this process may be streamlined by making it a seperate file, currently every line of code that has to be edited has been marked with comments containing **XYZ**.
Ctrl + F it to find them and you will be able to make the script work on, hopefully, anything that runs python.
  
The script works as such:
  
1. It creates a new webpage with a list of worlds to select by anyone visiting the site
2. Upon clicking any of the worlds on the selection page (or going directly to a specific link, such as 0.0.0.0:30000/curse-of-strahd), it will begin launching Foundry with the selected world as it's parameters.
3. After the world has no logged in users for a set amount of time (default 5 minutes), the script shuts down Foundry and reinstantiates itself, repeating the process.
