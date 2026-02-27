# Data Modeling Diagrams

Diagram types for modeling data structures, databases, and system architecture.

## ERD (Entity Relationship Diagram)

The `erd` diagram type uses a simple text notation for entity-relationship diagrams.

### Blog Database

```erd
[Person]
*name
height
weight
+birth_location_id

[Location]
*id
city
state
country

Person *--1 Location
```

### Library System

```erd
[Library]
*id
name
address

[Book]
*isbn
title
publication_year

[Author]
*id
first_name
last_name

[Member]
*id
name
email
join_date

[Loan]
*id
+book_isbn
+member_id
loan_date
return_date

Library 1--* Book
Author *--* Book
Member 1--* Loan
Book 1--* Loan
```

## DBML (Database Markup Language)

DBML is a simple language for defining database structures.

### E-Commerce Schema

```dbml
Table users {
  id integer [primary key]
  username varchar [unique, not null]
  email varchar [unique, not null]
  password_hash varchar [not null]
  created_at timestamp [default: `now()`]
}

Table products {
  id integer [primary key]
  name varchar [not null]
  description text
  price decimal [not null]
  stock integer [default: 0]
  category_id integer
}

Table orders {
  id integer [primary key]
  user_id integer [not null]
  status varchar [not null, note: 'pending, paid, shipped, delivered']
  total decimal
  created_at timestamp [default: `now()`]
}

Table order_items {
  id integer [primary key]
  order_id integer [not null]
  product_id integer [not null]
  quantity integer [not null]
  unit_price decimal [not null]
}

Table categories {
  id integer [primary key]
  name varchar [not null]
  parent_id integer
}

Ref: orders.user_id > users.id
Ref: order_items.order_id > orders.id
Ref: order_items.product_id > products.id
Ref: products.category_id > categories.id
Ref: categories.parent_id > categories.id
```

## Structurizr

Structurizr DSL provides a way to describe software architecture models using the C4 model.

### Web Application Architecture

```structurizr
workspace {
  model {
    user = person "User" "A user of the system"
    softwareSystem = softwareSystem "Online Store" {
      webapp = container "Web Application" "Delivers content" "React"
      api = container "API Server" "Handles business logic" "Node.js"
      database = container "Database" "Stores data" "PostgreSQL" "database"
      cache = container "Cache" "Session and query cache" "Redis" "database"
    }
    user -> webapp "Browses"
    webapp -> api "Makes API calls to"
    api -> database "Reads from and writes to"
    api -> cache "Caches data in"
  }
  views {
    container softwareSystem {
      include *
      autolayout lr
    }
  }
}
```
