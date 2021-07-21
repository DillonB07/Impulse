---
layout: page
title: Presets
nav_order: 4
---

# Impulse Presets

---


## What are presets?

Presets allow you to keep certain pieces of information inside the program so that you don't need to manually enter it each time you run the program

### Setting Presets

The current presets are:

* Username
    * Go to the `main.py` file and underneath the imports, you will see a variable called `USER`.
    * This variable is for use when launching applications. It must be the same as your username on your mac.
    * Not sure what your username is? Go to `/Users/` and see what your folder is called. That is your username.
    * Comment out the `input` line and on the line above, set it to this:
    ```python
    USER = 'USERNAME'
    ```
    
* Nick
    * Go to the `main.py` file and underneath the imports, you will see a variable called `NICK`.
    * This variable is used to address you.
    * Comment out the `input` line and set it to this:
    ```python
    NICK = 'YOUR PREFERRED NAME'
    ```
