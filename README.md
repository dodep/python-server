Currency Exchange API

1) git clone https://github.com/dodep/python-server.git
2) cd python-server
3) python server.py  
\*terminal output\*

    Server Running...

4) test: http://localhost:9090/?currency_amount=100&currency_from=USD&currency_to=RUB

currency_amount = integer from 1 to 999999  
currency_from = USD, EUR or RUB  
currency_to = USD, EUR or RUB  

test response:  

{  
    currency_rate: 76.7802503477  
    currency_date: "2020-04-03"  
    currency_amount: 100  
    currency_amount_converted: 7678.02503477  
    currency_from: "USD"  
    currency_to: "RUB"  
}

possible errors: 

400 {error: "currency amount required"}  
400 {error: "currency amount must be integer number that are greater then 0 and less then 1000000"}  
400 {error: "wrong query string"}  
400 {error: "currency must be USD, EUR or RUB"}  
404 {error: "no favicon"}  
500 {error: "internal server error"}  