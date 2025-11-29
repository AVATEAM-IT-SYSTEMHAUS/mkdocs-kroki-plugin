# UML & Class Diagrams

Omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet.

## Class Diagrams

Ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus.

### E-Commerce System

```plantuml
@startuml
class Customer {
  +String name
  +String email
  +String address
  +placeOrder()
  +cancelOrder()
  +viewOrderHistory()
}

class Order {
  +int orderId
  +Date orderDate
  +OrderStatus status
  +float totalAmount
  +addItem()
  +removeItem()
  +calculateTotal()
}

class OrderItem {
  +int quantity
  +float price
  +getSubtotal()
}

class Product {
  +int productId
  +String name
  +String description
  +float price
  +int stockQuantity
  +updateStock()
}

class Payment {
  +int paymentId
  +PaymentMethod method
  +float amount
  +Date timestamp
  +processPayment()
  +refund()
}

enum OrderStatus {
  PENDING
  PROCESSING
  SHIPPED
  DELIVERED
  CANCELLED
}

enum PaymentMethod {
  CREDIT_CARD
  DEBIT_CARD
  PAYPAL
  BANK_TRANSFER
}

Customer "1" -- "*" Order : places
Order "1" -- "*" OrderItem : contains
OrderItem "*" -- "1" Product : references
Order "1" -- "1" Payment : processes
@enduml
```

## Use Case Diagram

Ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat.

```plantuml
@startuml
left to right direction
actor Customer
actor Clerk

rectangle Checkout {
  Customer -- (Checkout)
  (Checkout) .> (Payment) : includes
  (Help) .> (Checkout) : extends
  (Checkout) -- Clerk
}
@enduml
```

## Entity Relationship

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium.

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER {
        int customer_id PK
        string name
        string email
        string phone
    }
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        int order_id PK
        int customer_id FK
        date order_date
        string status
        decimal total_amount
    }
    ORDER_ITEM {
        int order_item_id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal unit_price
    }
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"
    PRODUCT {
        int product_id PK
        string name
        string description
        decimal price
        int stock_quantity
    }
    CATEGORY ||--o{ PRODUCT : contains
    CATEGORY {
        int category_id PK
        string name
        string description
    }
```

## Component Diagram

Totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.

```plantuml
@startuml
package "Web Application" {
  [User Interface] as UI
  [Business Logic] as BL
  [Data Access Layer] as DAL
}

package "External Services" {
  [Payment Gateway] as PG
  [Email Service] as ES
  [Analytics] as AN
}

database "Database" {
  [User Data]
  [Product Catalog]
  [Order History]
}

UI --> BL
BL --> DAL
DAL --> [User Data]
DAL --> [Product Catalog]
DAL --> [Order History]
BL --> PG : process payments
BL --> ES : send notifications
BL --> AN : track events
@enduml
```

## Pirate Class Hierarchy

Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores.

```nomnoml
[Pirate|eyeCount: Int|raid();pillage()|
  [beard]--[parrot]
  [beard]-:>[foul mouth]
]

[<abstract>Marauder]<:--[Pirate]
[Pirate]- 0..7[mischief]
[jollyness]->[Pirate]
[jollyness]->[rum]
[jollyness]->[singing]
[Pirate]-> *[rum|tastiness: Int|swig()]
[Pirate]->[singing]
[singing]<->[rum]
```

## Gantt Chart

Eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet.

```mermaid
gantt
    title Project Development Timeline
    dateFormat  YYYY-MM-DD
    section Planning
    Requirements gathering       :a1, 2024-01-01, 14d
    System design               :a2, after a1, 10d
    section Development
    Backend development         :b1, 2024-01-25, 30d
    Frontend development        :b2, 2024-02-05, 25d
    Database setup             :b3, 2024-01-25, 7d
    section Testing
    Unit testing               :c1, after b1, 10d
    Integration testing        :c2, after b2, 7d
    UAT                       :c3, after c2, 5d
    section Deployment
    Staging deployment         :d1, after c3, 2d
    Production deployment      :d2, after d1, 1d
```

Consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.
