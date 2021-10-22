# zebrands-restful-apis
 flask restful api
 
 ### Running the API

To run this application, you will need Python 3.8 and [Pipenv](https://pipenv.readthedocs.io/en/latest/) installed locally. If you have then, you can issue the following commands:

1. virtualenv venv
2. pip install -r requirements.txt
3. python catalog/index.py  


## Docker-compose instructions

To install this app in your local machine please follow the instructions bellow.

1. Create a new network with `docker network create localnet`
3. Run `docker-compose up` command.


# use https://github.com/pypa/pipenv

# send emails use https://pythonhosted.org/Flask-Mail/

# view docs http://127.0.0.1:5000/swagger-ui/

# for test api use test_api_product.py and test_api_user.py

# view graphql http://127.0.0.1:5000/graphql

# using https://ariadnegraphql.org/

# example mutation

mutation{
  login(username: "adminApi@gmail.com", password:"zaq1ZAQ!")
  {
    token
    success
    errors
  }
}

# Product crud

query{
   listProducts
  {
    success
    errors
    product
    {
      sku
      name
      price
      brand
      created
    }
  }
}

# In mutation HTTP HEADERS add token from mutation login to authorized

{"Authorization":""}

mutation
{
   addProduct(name:"Lavadora", price: 1000, brand: "Ocean")
  {
    success
    errors
    product
    {
      sku
      name
      price
      brand
      created
    }
  }
}

mutation
{
  deleteProduct(sku:"911438b5-a463-457e-b794-fbc1940813b5")
  {
    success
    errors
    product
    {
      sku
      name
      price
      brand
      created
    }
  }
}

mutation
{
   updateProduct(sku:"911438b5-a463-457e-b794-fbc1940813b5", name:"Almohadas", price: 400, brand:"Luuna")
  {
    success
    errors
    product
    {
      sku
      name
      price
      brand
      created
    }
  }
}

# User crud
query
{
    listUsers 
  {
    success
    errors
    user
    {
      id
      email
      name
      password
      role
      idcreated
    }
  }
}

mutation
{
   addUser(email:"admin5Api@gmail.com", name:"admin5", password:"zaq1ZAQ!", role:"Admin")
  {
    success
    errors
    user
    {
      id
      email
      name
      password
      role
      idcreated
    }
  }
}

mutation
{
   updateUser(id:"ac9eeb52-63b7-413b-a310-de393998ca71", name:"Admin5", password:"1qazxsw2", role:"Admin")
  {
    success
    errors
    user
    {
      id
      email
      name
      password
      role
      idcreated
    }
  }
}


mutation
{
   deleteUser(id:"ac9eeb52-63b7-413b-a310-de393998ca71")
  {
    success
    errors
    user
    {
      id
      email
      name
      password
      role
      idcreated
    }
  }
}