#!binsh

echo  create redis internal database  

python /user/src/loadbal/script/loadin_apapsservers.py

uvicorn main:app --host 0.0.0.0 --port 5400