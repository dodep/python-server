import socket
import re
import datetime
import requests
import json
import threading

class CurrencyExServer:
    
    def start_server(self):
        server_socket = socket.socket()
        server_socket.bind(('',9090))
        server_socket.listen(1)
        print('\nServer Running...\n')
        
        while True:
            client_socket, client_addr = server_socket.accept()
            client_handler = threading.Thread(target=self.serve_connection,args=(client_socket,))
            client_handler.start()
        
    def server_response_func(self, status_code, response_body, client_socket):
        """Send response to client"""
        server_response = f'HTTP/1.1 {status_code}\nContent-type: application/json; charset=utf-8\n\n{json.dumps(response_body)}'
        client_socket.sendall(server_response.encode())
        client_socket.close()
        
    def URI_validation(self, request_URI, client_socket):
        """URI validation.
        
        First check if favicon
        then check if currency amount is correct,
        then check if selected a valid currencies,
        then check the whole URI string
        """
        # favicon check:
        f_icon_pattern = re.compile(r'/favicon.ico')
        f_icon_check = f_icon_pattern.search(request_URI)
        
        if f_icon_check:
            return self.server_response_func(404, {'error':'no favicon'}, client_socket)
        
        # currency amount check:
        currency_amount_pattern = re.compile(r'currency_amount=\d+')
        check_currency_amount = currency_amount_pattern.search(request_URI)
        
        if check_currency_amount:
            currency_amount_vl = float(check_currency_amount.group(0).split('=')[1])
            if currency_amount_vl > 999999 or currency_amount_vl == 0:
                return self.server_response_func(400, {'error':'currency amount must be integer number that are greater then 0 and less then 1000000'}, client_socket)
        else:
            return self.server_response_func(400, {'error':'currency amount required'}, client_socket)

        # check currencies:
        currency_pattern = re.compile(r'currency_from=(USD|RUB|EUR)&currency_to=(USD|RUB|EUR)')
        check_currency = currency_pattern.search(request_URI)
            
        if not check_currency:
            return self.server_response_func(400, {'error':'currency must be USD, EUR or RUB'}, client_socket)

        # check whole URI:
        pattern = re.compile(r'/\?currency_amount=\d+&currency_from=(USD|RUB|EUR)&currency_to=(USD|RUB|EUR)')
        request_URI_match = pattern.match(request_URI)
        if not request_URI_match:
            return self.server_response_func(400, {'error':'wrong query string'}, client_socket)
            
        return True

    def serve_connection(self, client_socket):
        try:
            client_request = client_socket.recv(1024).decode()
            headers = client_request.split('\n')
            request_URI = headers[0].split()[1]
            
            if self.URI_validation(request_URI, client_socket):
                query_dictionary = {}
                
                for i in request_URI.replace('/?', '').split('&'):
                    query_dictionary[i.split('=')[0]] = i.split('=')[1]
                
                currency_amount = float(query_dictionary.get('currency_amount'))
                currency_from = query_dictionary.get('currency_from')
                currency_to = query_dictionary.get('currency_to')
                
                api_response = requests.get(f'https://api.exchangeratesapi.io/latest?symbols={currency_to}&base={currency_from}')
                api_response_dict = json.loads(api_response.text)
                currency_rate = list(api_response_dict.get('rates').values())[0]

                server_response_dictionary = {
                    'currency_rate': currency_rate,
                    'currency_date': api_response_dict.get('date'),
                    'currency_amount': currency_amount,
                    'currency_amount_converted': currency_amount * currency_rate,
                    'currency_from': currency_from,
                    'currency_to': currency_to
                }
                
                self.server_response_func(200, server_response_dictionary, client_socket)
        except:
            self.server_response_func(500, {'error':'internal server error'}, client_socket)
server = CurrencyExServer()
server.start_server()