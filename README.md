# PrivaLise 
### Social Media Network Focuses On Data Security And Being Community Driven Web App

## The Main Idea:
Can you imagine a centralized, but privacy-respecting social network? One that is modern, easy to use, fast and provides security and protection for everyone. That is why we created PrivaLise!

Encrypted credentials, 2 factor authentication, no associated personal information to hack... To Put It Simply: The Web App will not record anything about its users. <br/>
We actively avoid using any 3rd party software, such as google APIs, google analytics, any FAANG framework (React, Vue...), so rest assured that you will be totally anonymous :D

We also plan on creating an onion version of the web, so stay tunned!!

## Community: contribute or hang out with the developers!
Join our [discord server](https://discord.gg/2XzgH4bZYp) now!

## Support: Donate Anonymously To Support The Development Of This Awesome Project
bitcoin: bc1qvyfd5flhkkaxrgmscx3gzhrsrt72srgy3agjkl

![Qr Code](https://user-images.githubusercontent.com/87126411/126029544-9a5b1f67-9c86-40e2-baf3-7202c40707bb.png)

monero: 89xGzwEh8MiSbi1dLWRzijXGsi3AX5WadTQztxtiN63yKww7n9PYZiw1wjdgGKWy7ueDh5MrYZm6EggBv2ErGKH1V9Lujjh

![monero](https://user-images.githubusercontent.com/78929105/128041075-24a358a8-8b01-4099-8d4b-45247f5ea7f7.png)


Thanks :D
## The Technology Behind It:
   * Python 3.9.2
   * Django 2.2.22
   * Pure HTML/CSS/JS

## Main Features:
   * Sign IN/UP/OUT
   * Post CRUD
   * Update Username / Profile Pic
   * Notifications
   * Infinite Scroll On The Home Page
   * Password Recovery / Change
   * Follow/Unfollow users
   * Commenting And Replying To Comments
   * Hashtags And Mentions
   * Dark/Light Theme
   * Public Profile For Each User With a profle pic
   * Ajax Powered Likes/Dislikes with counter
   * 2 factor authentication

## New front-end
The entire front-end is being completely re-designed from the ground up. This may cause some inconsistencies or non-responsive parts of it, as well as sudden changes in design (hopefully for the better).

Any feedback or suggestion is very much appreciated and can be sent to [the discord server](https://discord.gg/2XzgH4bZYp).

 ## Set Up: 
  * Clone The Repository `git clone https://github.com/privalise/social-network.git && cd social-network`
  * Install Requirements `pip install -r requirements.txt && cd privalises`
  * Let's Migrate And Make Migrations `python manage.py makemigrations && python manage.py migrate`
  * Now Finally We Will Run The Server `python manage.py runserver`
  
 ### Additional Steps:
  1. Create '.env' file in the root directory
  2. Specify The Following
	  * email (Add The EMAIL_HOST_USER)
	  * pass (Specify The EMAIL_HOST_PASSWORD)
	  * port  (Specify The EMAIL_PORT)
	  * hash  (Specify The SECRET_KEY)
	  * backend (Specify The EMAIL_BACKEND)
	  * host (Specify The EMAIL_HOST)
	  * tls (Specify The EMAIL_USE_TLS)
	 ### In The End It Should Look Like This:
	  ```python
	  email=email@email.email
	  pass=password
	  hash=gjkmjgbkjbgmoirejoibjgboikejrgkjstojmsvoiigormjoiysmdfvmg
	  port=587
	  tls=True
	  host=smtp.provider.com
	  backend=django.core.mail.backends.smtp.EmailBackend	
	  ```

# LICENSE
	Privalise, A Secure Privacy Friendly Social Network
	Copyright (C) 2021 Mohab Gabber
	
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	any later version.
	
	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.
	










