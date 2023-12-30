# zoo app  
- flask sqlite app with sqlalchemy  
- migrate implemented  


# features:  
- signup - done  
- login / logout - impemented with session - done  
- display zoo animals - done  
- search animal - done  
- add animal - admin only - done  
- update animal - admin only - done  
- delete animal - admin only - done  


# toDo:  
- encrypt password  
- implement Flask-Login  


# run app:  


- macOs/Linux:  

git clone https://github.com/novodevz/zoo_flskapp_sqlite_alchemy.git  
cd zoo_flskapp_sqlite_alchemy.git  
python -m venv venv  
source venv/Scripts/activate  
pip install -r requirements.txt  
py db_mdl.py  
py app.py  

- windows:  

git clone https://github.com/novodevz/zoo_flskapp_sqlite_alchemy.git  
cd zoo_flskapp_sqlite_alchemy.git  
python -m venv venv  
venv/Scripts/activate  
pip install -r requirements.txt  
py db_mdl.py  
py app.py  


go to `http://localhost:5000`  

admin email address: admin@zoo.com  
at admin signup, assign admin password of your choice  

