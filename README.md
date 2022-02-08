# PrivaLise 
### Social Media Network Focuses On Data Security And Being Community Driven Web App

## The Main Idea:
Can you imagine a centralized, but privacy-respecting social network? One that is modern, easy to use, fast and provides security and protection for everyone. That is why we created PrivaLise!

2 factor authentication via PGP, monero integration, no associated personal information to hack... To Put It Simply: The Web App will not record anything about its users. <br/>
We'll always avoid using any 3rd party software, such as google APIs, google analytics, any FAANG framework (React, Vue...), so rest assured that you will be totally anonymous :D

it's also perfect as an onion service, bc the website doesn't have any js in it, so it can work in tor with the safest mode enabled.

## The Technology Behind It:
   * Python 3.10
   * Django 4
   * Pure HTML/CSS

## Main Features:
   It has all the standard features for a social media like: sign in/up/out, post CRUD, coment CRUD, likes/dislikes, follow/unfollow, public profile for users, etc ... but we added additional privacy-focused features like: monero address for every user, public key, fingerprint, 2FA via PGP, xmppserver, etc... we also added human verification in various places to increase security. and currently we are working on a Punishment mechanism for users who violate the laws of the network, every user will have to send a very small monero amount (1$) to be able to interact else their permissions will be read-only, this amount will be saved in their account and if they harrased, bullied any other user the amount they sent will be sent to the victim, and the network's wallet secret view key (the one that receives all this money) will be public to enhance trust in the platform.

## The front-end
The frontend is mostly made (like 90%) by [margual56](https://github.com/margual56)

## Set Up: 
  * Clone The Repository `git clone https://github.com/privalise-network.git && cd privalise-network`
  * Install Requirements `pip install -r requirements.txt`
  * you'll have to create a .env file in the root directory of the app, and specify `debug` and `secret_key`
  * Let's Make Migrations And Migrate  `python manage.py makemigrations mod && python manage.py makemigrations posts && python manage.py makemigrations users && python manage.py migrate`
  * you need to be running `monero-wallet-rpc` in the background in order for certain functionalities to work
  * Now Finally We Will Run The Server `python manage.py runserver`
  * NOTE: you need to download `gnupg` for 2 factor-authentication and some other functionalities to work

# LICENSE
	Privalise, A Secure Privacy Friendly Social Network
	Copyright (C) 2022 Mohab Gabber
	
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	any later version.
	
	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.
