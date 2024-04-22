# INFSCI 2710 - Database Management Systems

## Final Project Design Document 



### **Title page**

#### Team

- Jiazhe Wen([jiw321@pitt.edu](mailto:jiw321@pitt.edu))

- Zhiyun Chen([zhc148@pitt.edu](mailto:zhc148@pitt.edu))

- Xianglong Xu([xix110@pitt.edu](mailto:xix110@pitt.edu))

#### Course name: INFSCI 2710 SEC1090 DATABASE MANAGEMENT

#### Instructor: Dmitriy Babichenko 

#### Date: 04/22/2024



### Introduction/Abstract

- Simplifying property search and management for renters and buyers. Explore, list, and analyze residential and commercial properties with ease.
- By providing a comprehensive and user-friendly platform, we empower users to effortlessly navigate the often complex and time-consuming process of finding and managing properties. Whether it's assisting renters in finding their dream home or helping buyers identify lucrative investment opportunities, our app streamlines the entire journey. 



### E-R Model

![image-20240421220851839](https://cdn.jsdelivr.net/gh/Sean652039/pic_bed@main/uPic/image-20240421220851839.png)

![image-20240421220938165](https://cdn.jsdelivr.net/gh/Sean652039/pic_bed@main/uPic/image-20240421220938165.png)



### Business rules

| **Entity 1**  | **Entity 2**   | **Cardinality on Entity 1 side** | **Cardinality on Entity 2 side** | **Business Rule(s)**                                         |
| ------------- | -------------- | -------------------------------- | -------------------------------- | ------------------------------------------------------------ |
| User          | UserType       | m                                | n                                | Our system allows each user to have multiple types. A type can belong to multiple user. |
| User          | Password       | 1                                | 1                                | Our system allows each user to have only one password to avoid ambiguity. |
| User          | Review         | 1                                | m                                | Our system allows each user to have multiple reviews. But a review can only belong to one user. |
| User          | Property       | 1                                | m                                | Our system allows each user to have multiple properties. But a property can only belong to one user. |
| User          | Contract       | 1                                | m                                | Our system allows each user to have multiple contracts. But a party of a contract can only belong to one user. |
| User          | Appointments   | 1                                | m                                | Our system allows each user to have multiple Appointments. But a party of appointment can only belong to one user. |
| Property      | Appointments   | 1                                | m                                | Our system allows each property to have multiple Appointments. But a appointment can only contain one property. |
| Property      | Review         | 1                                | m                                | Our system allows each property to have multiple reviews. But a review can only belong to one property. |
| Property      | Address        | 1                                | m                                | Our system allows each property to have only one address(street line). But a address(street line) can belong to many properties. |
| Property      | PropertyDetail | 1                                | 1                                | Our system allows each property to have only one detail, to avoid ambiguity. |
| Property      | MarketListings | 1                                | 1                                | Our system allows each property to have only one MarketListings, to avoid ambiguity. |
| Property      | Contract       | 1                                | m                                | Our system allows each property belong to multiple contracts. But a contract can only contain one property. |
| Property      | Image          | 1                                | 1                                | Our system allows each property to have only one image, to avoid ambiguity. |
| ZipCode       | Address        | 1                                | m                                | Our system allows each ZipCode to contain multiple addresses. But a address can only belong one property. |
| City          | Address        | 1                                | m                                | Our system allows each city to contain multiple addresses. But a address can only belong one city. |
| State         | City           | 1                                | m                                | Our system allows each state to contain multiple cities. But a city can only belong one state. |
| Payment       | Contract       | 1                                | m                                | Our system allows each payment to be used by multiple contracts. But a contract can only have one payment. |
| PaymentMethod | Payment        | 1                                | m                                | Our system allows each payment method to be used by multiple payments. But a payment can only have one payment method. |



### Additional Notes

#### Transaction Design:

 In the database, we have designed a transaction that manages the creation of Contract and Payment records and associates these two records in the PaymentOfContract table through the CreateContractAndPayment procedure. It accepts five parameters, the contract price, the ID of the first party to the contract, the ID of the second party to the contract, the ID of the house involved in the contract. and the amount of the payment, inserts the completed contract information into the database, and ensures that the data is correctly inserted into the three tables through encapsulation and rollback steps that ensure the consistency and integrity of the database state.

#### View Design:
 In this database, we added User and Property Details View,  User and Property Details View and PropertyInfo view respectively to speed up the process during home rental and user page queries.

- User and Property Details View joins the User, Property, and PropertyDetail tables to provide a consolidated details view of the properties associated with a user. This view makes it more efficient to display details of all related properties in the user's personal interface.
-  Property and Market Listings View connects the Property and MarketListings tables to display the market listing information for a property, providing a quick overview of the property listing information.
- PropertyInfo joins several tables to consolidate details about properties and their locations. This view integrates data from the Property, PropertyLocateAddress, Address, AddressLocateCity, City, and PropertyDetail tables. It facilitates the retrieval of comprehensive information about properties, including their descriptions, year built, square footage, number of bedrooms and bathrooms, as well as the associated city name. By joining these tables, the view offers a consolidated perspective on property details, streamlining the process of accessing essential property information. This view could be particularly useful for tasks such as property management, analysis, or reporting where a comprehensive overview of property details is required.

#### Index

To optimize the performance of the property leasing system, we've created a series of indexes based on the application's usage patterns. 

- indexes have been established on primary key columns to expedite access to core tables such as Property, User, Appointments, Contract, and Review. This facilitates swift retrieval of specific row data within these tables, enhancing query efficiency. 
- we've crafted indexes on foreign key columns frequently used in join operations, thus accelerating join processes and improving query efficiency. For instance, when linking Contract and Review tables, indexes aid in swiftly locating associations between contracts and corresponding properties or users. 
- indexes have been set on columns frequently utilized in WHERE clauses, like appointment times and contract IDs, to expedite related query operations, resulting in quicker system responsiveness and smoother user experiences.

#### Demo

- Login 

<img src="https://cdn.jsdelivr.net/gh/Sean652039/pic_bed@main/uPic/image-20240422185301245.png" alt="image-20240422185301245" style="zoom:50%;" />

- Register

<img src="https://cdn.jsdelivr.net/gh/Sean652039/pic_bed@main/uPic/image-20240422185422122.png" alt="image-20240422185422122" style="zoom:50%;" />

- Tenant Dashboard

![image-20240422185331372](https://cdn.jsdelivr.net/gh/Sean652039/pic_bed@main/uPic/image-20240422185331372.png)

- Landlord Dashboard

![image-20240422185511037](https://cdn.jsdelivr.net/gh/Sean652039/pic_bed@main/uPic/image-20240422185511037.png)