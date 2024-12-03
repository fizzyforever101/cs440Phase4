-- CS4400: Introduction to Database Systems (Fall 2024)
-- Project Phase III: Stored Procedures SHELL [v0] Monday, Oct 21, 2024
set global transaction isolation level serializable;
set global SQL_MODE = 'ANSI,TRADITIONAL';
set names utf8mb4;
set SQL_SAFE_UPDATES = 0;

use business_supply;
-- -----------------------------------------------------------------------------
-- stored procedures and views
-- -----------------------------------------------------------------------------
/* Standard Procedure: If one or more of the necessary conditions for a procedure to
be executed is false, then simply have the procedure halt execution without changing
the database state. Do NOT display any error messages, etc. */

-- [1] add_owner()
-- -----------------------------------------------------------------------------
/* This stored procedure creates a new owner.  A new owner must have a unique
username.  Also, the new owner is not allowed to be an employee. */
-- -----------------------------------------------------------------------------
drop procedure if exists add_owner;
delimiter //
create procedure add_owner (in ip_username varchar(40), in ip_first_name varchar(100),
	in ip_last_name varchar(100), in ip_address varchar(500), in ip_birthdate date)
sp_main: begin
    -- ensure new owner has a unique username
    -- check if new owner username matches an employee's username or an existing owner
    if ip_username in (select username from employees) then leave sp_main;
	elseif ip_username in (select username from business_owners) then leave sp_main;
    else insert into users (username, first_name, last_name, address, birthdate)
    values (ip_username, ip_first_name, ip_last_name, ip_address, ip_birthdate);
    insert into business_owners (username) values (ip_username);
    end if;
end //
delimiter ;

-- [2] add_employee()
-- -----------------------------------------------------------------------------
/* This stored procedure creates a new employee without any designated driver or
worker roles.  A new employee must have a unique username unique tax identifier. */
-- -----------------------------------------------------------------------------
drop procedure if exists add_employee;
delimiter //
create procedure add_employee (in ip_username varchar(40), in ip_first_name varchar(100),
	in ip_last_name varchar(100), in ip_address varchar(500), in ip_birthdate date,
    in ip_taxID varchar(40), in ip_hired date, in ip_employee_experience integer,
    in ip_salary integer)
sp_main: begin
    -- ensure new employee has a unique username
    -- ensure new employee has a unique tax identifier
    if ip_username in (select username from employees) then leave sp_main;
    elseif ip_taxID in (select taxID from employees) then leave sp_main;
    else insert into users (username, first_name, last_name, address, birthdate)
    values (ip_username, ip_first_name, ip_last_name, ip_address, ip_birthdate);
    insert into employees (username, taxID, hired, experience, salary)
    values (ip_username, ip_taxID, ip_hired, ip_employee_experience, ip_salary);
    end if;
end //
delimiter ;

-- [3] add_driver_role()
-- -----------------------------------------------------------------------------
/* This stored procedure adds the driver role to an existing employee.  The
employee/new driver must have a unique license identifier. */
-- -----------------------------------------------------------------------------
drop procedure if exists add_driver_role;
delimiter //
create procedure add_driver_role (in ip_username varchar(40), in ip_licenseID varchar(40),
	in ip_license_type varchar(40), in ip_driver_experience integer)
sp_main: begin
    -- ensure employee exists
    -- ensure new driver has a unique license identifier
    if ip_username not in (select username from employees) then leave sp_main;
    elseif ip_licenseID in (select licenseID from drivers) then leave sp_main;
    else insert into drivers (username, licenseID, license_type, successful_trips) 
    values (ip_username, ip_licenseID, ip_license_type, ip_driver_experience);
    end if;
end //
delimiter ;

-- [4] add_worker_role()
-- -----------------------------------------------------------------------------
/* This stored procedure adds the worker role to an existing employee. */
-- -----------------------------------------------------------------------------
drop procedure if exists add_worker_role;
delimiter //
create procedure add_worker_role (in ip_username varchar(40))
sp_main: begin
    -- ensure employee exists
    if ip_username not in (select username from employees) then leave sp_main;
    else insert into workers (username) values (ip_username);
    end if;
end //
delimiter ;

-- [5] add_product()
-- -----------------------------------------------------------------------------
/* This stored procedure creates a new product.  A new product must have a
unique barcode. */
-- -----------------------------------------------------------------------------
drop procedure if exists add_product;
delimiter //
create procedure add_product (in ip_barcode varchar(40), in ip_name varchar(100),
	in ip_weight integer)
sp_main: begin
	-- ensure new product doesn't already exist
    if ip_barcode in (select barcode from products) then leave sp_main;
    else insert into products (barcode, iname, weight) values (ip_barcode, ip_name, ip_weight);
    end if;
end //
delimiter ;

-- [6] add_van()
-- -----------------------------------------------------------------------------
/* This stored procedure creates a new van.  A new van must be assigned 
to a valid delivery service and must have a unique tag.  Also, it must be driven
by a valid driver initially (i.e., driver works for the same service), but the driver
can switch the van to working as part of a swarm later. And the van's starting
location will always be the delivery service's home base by default. */
-- -----------------------------------------------------------------------------
drop procedure if exists add_van;
delimiter //
create procedure add_van (in ip_id varchar(40), in ip_tag integer, in ip_fuel integer,
	in ip_capacity integer, in ip_sales integer, in ip_driven_by varchar(40))
sp_main: begin

	DECLARE ip_located_at varchar(40);
    
    if (ip_capacity is null or ip_sales is null or ip_driven_by is null or ip_fuel is null or ip_id is null or ip_tag is null) then 
		leave sp_main;
    end if;
    
    -- ensure that the delivery service exists
	if (select count(*) from delivery_services where id = ip_id) = 0 then
		leave sp_main;
	end if;
    
    select home_base INTO ip_located_at from delivery_services where id = ip_id;

	-- ensure new van doesn't already exist
	if (select count(*) from vans where tag = ip_tag) > 0 then
		leave sp_main;
    end if;
    
    -- ensure that a valid driver will control the van
    if (select count(*) from drivers where username = ip_driven_by) = 0 then
		leave sp_main;
    end if;
    
	if (select count(*) from vans where driven_by = ip_driven_by and id != ip_id) > 0 then
        leave sp_main;
    end if;

    insert into vans (id, tag, fuel, capacity, sales, driven_by, located_at)
    values (ip_id, ip_tag, ip_fuel, ip_capacity, ip_sales, ip_driven_by, ip_located_at);
    
end //
delimiter ;

-- [7] add_business()
-- -----------------------------------------------------------------------------
/* This stored procedure creates a new business.  A new business must have a
unique (long) name and must exist at a valid location, and have a valid rating.
And a resturant is initially "independent" (i.e., no owner), but will be assigned
an owner later for funding purposes. */
-- -----------------------------------------------------------------------------
drop procedure if exists add_business;
delimiter //
create procedure add_business (in ip_long_name varchar(40), in ip_rating integer,
	in ip_spent integer, in ip_location varchar(40))
sp_main: begin
	-- ensure new business doesn't already exist
    if (select count(*) from businesses where long_name = ip_long_name) > 0 then 
		leave sp_main;
    end if;
    
    -- ensure that the location is valid
    if (select count(*) from locations where label = ip_location) = 0 then
		leave sp_main;
    end if;
    
    -- ensure that the rating is valid (i.e., between 1 and 5 inclusively)
    if ip_rating < 1 or ip_rating > 5 then
		leave sp_main;
    end if;
    
    insert into businesses
    values (ip_long_name, ip_rating, ip_spent, ip_location);
    
end //
delimiter ;

-- [8] add_service()
-- -----------------------------------------------------------------------------
/* This stored procedure creates a new delivery service.  A new service must have
a unique identifier, along with a valid home base and manager. */
-- -----------------------------------------------------------------------------
drop procedure if exists add_service;
delimiter //
create procedure add_service (in ip_id varchar(40), in ip_long_name varchar(100),
	in ip_home_base varchar(40), in ip_manager varchar(40))
sp_main: begin
	-- ensure new delivery service doesn't already exist
    if (select count(*) from delivery_services where id = ip_id) > 0 then
		leave sp_main;
    end if;
    
    -- ensure that the home base location is valid
    if (select count(*) from locations where label = ip_home_base) = 0 then
		leave sp_main;
    end if;
    
    -- ensure that the manager is valid
    if (select count(*) from employees where username = ip_manager) = 0 then 
		leave sp_main;
    end if;
    
    insert into delivery_services
    values(ip_id, ip_long_name, ip_home_base, ip_manager);
    
end //
delimiter ;

-- [9] add_location()
-- -----------------------------------------------------------------------------
/* This stored procedure creates a new location that becomes a new valid van
destination.  A new location must have a unique combination of coordinates.  We
could allow for "aliased locations", but this might cause more confusion that
it's worth for our relatively simple system. */
-- -----------------------------------------------------------------------------
drop procedure if exists add_location;
delimiter //
create procedure add_location (in ip_label varchar(40), in ip_x_coord integer,
	in ip_y_coord integer, in ip_space integer)
sp_main: begin
	-- ensure new location doesn't already exist
    if (select count(*) from locations where label = ip_label) > 0 then
		leave sp_main;
    end if;

    -- ensure that the coordinate combination is distinct
    if (select count(*) from locations where x_coord = ip_x_coord and y_coord = ip_y_coord) > 0 then
		leave sp_main;
    end if;
    
    insert into locations
    values (ip_label, ip_x_coord, ip_y_coord, ip_space);

end //
delimiter ;

-- [10] start_funding()
-- -----------------------------------------------------------------------------
/* This stored procedure opens a channel for a business owner to provide funds
to a business. If a different owner is already providing funds, then the current
owner is replaced with the new owner.  The owner and business must be valid. */
-- -----------------------------------------------------------------------------
drop procedure if exists start_funding;
delimiter //
create procedure start_funding (in ip_owner varchar(40), in ip_amount integer, in ip_long_name varchar(40), in ip_fund_date date)
sp_main: begin
	-- ensure the owner and business are valid
    if (select count(*) from business_owners where username = ip_owner) = 0 then
		leave sp_main;
    end if;
    
    if (select count(*) from businesses where long_name = ip_long_name) = 0 then 
		leave sp_main;
    end if;
    
	insert into fund (username, invested, invested_date, business) values (ip_owner, ip_amount, ip_fund_date, ip_long_name);
    
end //
delimiter ;

-- [11] hire_employee()
-- -----------------------------------------------------------------------------
/* This stored procedure hires an employee to work for a delivery service.
Employees can be combinations of workers and drivers. If an employee is actively
controlling vans or serving as manager for a different service, then they are
not eligible to be hired.  Otherwise, the hiring is permitted. */
-- -----------------------------------------------------------------------------
drop procedure if exists hire_employee;
delimiter //
create procedure hire_employee (in ip_username varchar(40), in ip_id varchar(40))
sp_main: begin
-- ensure that the employee hasn't already been hired
-- ensure that the employee and delivery service are valid
-- ensure that the employee isn't a manager for another service
-- ensure that the employee isn't actively controlling vans for another service
if ip_id not in (select id from delivery_services) then leave sp_main; end if;
if ip_username not in (select username from employees) then leave sp_main; end
if;
if ip_id not in (select id from work_for where ip_username = username)
and ip_username not in (select manager from delivery_services)
then insert into work_for (username, id) values (ip_username, ip_id);
end if;
end //
delimiter ;

-- [12] fire_employee()
-- -----------------------------------------------------------------------------
/* This stored procedure fires an employee who is currently working for a delivery
service.  The only restrictions are that the employee must not be: [1] actively
controlling one or more vans; or, [2] serving as a manager for the service.
Otherwise, the firing is permitted. */
-- -----------------------------------------------------------------------------
drop procedure if exists fire_employee;
delimiter //
create procedure fire_employee (in ip_username varchar(40), in ip_id varchar(40))
sp_main: begin
	if (ip_username is null or ip_id is null) then
		leave sp_main;
    end if;
	-- ensure that the employee is currently working for the service 
	if (select count(*) from work_for where username = ip_username and id = ip_id) = 0 
		then leave sp_main; 
    end if;
    
    -- ensure that the employee isn't an active manager
     if (select count(*) from delivery_services where manager = ip_username) > 0 then
		leave sp_main; 
     end if;
     
     if (select count(*) from vans where driven_by = ip_username and id = ip_id) > 0 then
        leave sp_main;
     end if;
     
     
		
	delete from work_for where username = ip_username and id = ip_id;
    
end //
delimiter ;

-- [13] manage_service()
-- -----------------------------------------------------------------------------
/* This stored procedure appoints an employee who is currently hired by a delivery
service as the new manager for that service.  The only restrictions are that: [1]
the employee must not be working for any other delivery service; and, [2] the
employee can't be driving vans at the time.  Otherwise, the appointment to manager
is permitted.  The current manager is simply replaced.  And the employee must be
granted the worker role if they don't have it already. */
-- -----------------------------------------------------------------------------
drop procedure if exists manage_service;
delimiter //
create procedure manage_service (in ip_username varchar(40), in ip_id varchar(40))
sp_main: begin
-- 1 ensure that the employee is currently working for the service
	if (select count(*) from work_for where username = ip_username and id = ip_id) = 0 then
		leave sp_main;
    end if;

-- 2 ensure that the employee is not driving any vans
	if (select count(*) from vans where driven_by = ip_username ) > 0 then
		leave sp_main;
    end if;

-- 3 ensure that the employee isn't working for any other services
	if (select count(*) from work_for where username = ip_username and id != ip_id) > 0 then
		leave sp_main;
	end if;

-- 4 add the worker role if necessary
	if (select count(*) from workers where username = ip_username) = 0 then
		insert into workers (username) values (ip_username); 
	end if;

	update delivery_services set manager = ip_username where id = ip_id;
end //
delimiter ;

-- [14] takeover_van()
-- -----------------------------------------------------------------------------
/* This stored procedure allows a valid driver to take control of a van owned by 
the same delivery service. The current controller of the van is simply relieved 
of those duties. */
-- -----------------------------------------------------------------------------
drop procedure if exists takeover_van;
delimiter //
create procedure takeover_van (in ip_username varchar(40), in ip_id varchar(40), in ip_tag integer)
sp_main: begin
	-- ensure that the driver is not driving for another service
	-- ensure that the selected van is owned by the same service
	-- ensure that the employee is a valid driver
    
    if (select count(*) from vans where driven_by = ip_username and id != ip_id) > 0 then
		leave sp_main; 
    end if;
    
    if (select count(*) from drivers where username = ip_username) = 0 then 
		leave sp_main; 
    end if;
    
    if (select count(*) from vans where id = ip_id and tag = ip_tag) = 0 then 
		leave sp_main; 
    end if;
    
    update vans set driven_by = ip_username where id = ip_id and tag = ip_tag;
end //
delimiter ;

-- [15] load_van()
-- -----------------------------------------------------------------------------
/* This stored procedure allows us to add some quantity of fixed-size packages of
a specific product to a van's payload so that we can sell them for some
specific price to other businesses.  The van can only be loaded if it's located
at its delivery service's home base, and the van must have enough capacity to
carry the increased number of items.

The change/delta quantity value must be positive, and must be added to the quantity
of the product already loaded onto the van as applicable.  And if the product
already exists on the van, then the existing price must not be changed. */
-- -----------------------------------------------------------------------------
drop procedure if exists load_van;
delimiter //
create procedure load_van (in ip_id varchar(40), in ip_tag integer, in ip_barcode
varchar(40), in ip_more_packages integer, in ip_price integer)
sp_main: begin


declare ip_weight int;

-- ensure that the van being loaded is owned by the service
-- ensure that the product is valid
-- ensure that the van is located at the service home base
-- ensure that the quantity of new packages is greater than zero
-- ensure that the van has sufficient capacity to carry the new packages

-- add more of the product to the van

if ip_barcode not in (select barcode from products) or ip_tag not in (select tag from vans where id = ip_id) then 
	leave sp_main; 
    end if;
if (select located_at from vans where tag = ip_tag and id = ip_id) not in (select home_base from delivery_services where id = ip_id) then 
	leave sp_main;
    end if;
select weight into ip_weight from products where barcode = ip_barcode;
if ip_more_packages > 0 and 
   (ip_more_packages + 
   coalesce((select sum(quantity) from contain where id = ip_id and tag = ip_tag), 0)) <= 
   (select capacity from vans where tag = ip_tag and id = ip_id) then
	--  update vans 
-- 	set capacity = capacity - ip_more_packages 
-- 		where tag = ip_tag and id = ip_id;
    
	if ip_barcode in (select barcode from contain where tag = ip_tag and id= ip_id) then
		update contain 
			set quantity = quantity + ip_more_packages 
			where tag = ip_tag and id = ip_id;
	else
		insert into contain(id, tag, barcode, quantity, price) values
		(ip_id, ip_tag, ip_barcode, ip_more_packages, ip_price);
	end if;
end if;
end //
delimiter ;

end //
delimiter ;

-- [16] refuel_van()
-- -----------------------------------------------------------------------------
/* This stored procedure allows us to add more fuel to a van. The van can only
be refueled if it's located at the delivery service's home base. */
-- -----------------------------------------------------------------------------
drop procedure if exists refuel_van;
delimiter //
create procedure refuel_van (in ip_id varchar(40), in ip_tag integer, in ip_more_fuel integer)
sp_main: begin
	-- ensure that the van being switched is valid and owned by the service
    if (select count(*) from vans where (id = ip_id and tag = ip_tag)) = 0 then
		leave sp_main;
	end if;
    -- ensure that the van is located at the service home base
    if (select located_at from vans where (id = ip_id and tag = ip_tag)) <> (select home_base from delivery_services where id = ip_id) then
		leave sp_main;
	end if;

	update vans 
    set fuel = fuel + ip_more_fuel
    where id = ip_id and tag = ip_tag;
end //
delimiter ;

-- [17] drive_van()
-- -----------------------------------------------------------------------------
/* This stored procedure allows us to move a single van to a new
location (i.e., destination). This will also update the respective driver's 
experience and van's fuel. The main constraints on the van(s) being able to 
move to a new  location are fuel and space.  A van can only move to a destination
if it has enough fuel to reach the destination and still move from the destination
back to home base.  And a van can only move to a destination if there's enough
space remaining at the destination. */
-- -----------------------------------------------------------------------------
drop function if exists fuel_required;
delimiter //
create function fuel_required (ip_departure varchar(40), ip_arrival varchar(40))
	returns integer reads sql data
begin
	if (ip_departure = ip_arrival) then return 0;
    else return (select 1 + truncate(sqrt(power(arrival.x_coord - departure.x_coord, 2) + power(arrival.y_coord - departure.y_coord, 2)), 0) as fuel
		from (select x_coord, y_coord from locations where label = ip_departure) as departure,
        (select x_coord, y_coord from locations where label = ip_arrival) as arrival);
	end if;
end //
delimiter ;

drop procedure if exists drive_van;
delimiter //
create procedure drive_van (in ip_id varchar(40), in ip_tag integer, in ip_destination varchar(40))
sp_main: begin
	declare fuel_needed_destination INT;
    declare spaces_filled INT;
    declare fuel_needed_home INT;
    declare fuel_needed INT;
    -- ensure that the destination is a valid location
    if(select count(*) from locations where label = ip_destination) = 0 then 
		leave sp_main;
	end if;
    -- ensure that the van isn't already at the location
    if (select located_at from vans where id = ip_id and tag = ip_tag) = ip_destination then
		leave sp_main;
	end if;
    
    set fuel_needed_destination = fuel_required((select located_at from vans where id = ip_id and tag = ip_tag), ip_destination);
    set fuel_needed_home = fuel_required(ip_destination, (select home_base from delivery_services where id = ip_id));
    set fuel_needed = fuel_needed_destination + fuel_needed_home;
    -- ensure that the van has enough fuel to reach the destination and (then) home base
    if (select fuel from vans where id = ip_id and tag = ip_tag) < fuel_needed then 
		leave sp_main;
	end if;
    -- ensure that the van has enough space at the destination for the trip
    select count(*) into spaces_filled from vans where located_at = ip_destination;
    if (select space from locations where label = ip_destination) - spaces_filled < 1 then 
		leave sp_main;
	end if;
    
    update vans
    set located_at = ip_destination
    where id = ip_id and tag = ip_tag;
    
    update vans
    set fuel = fuel - fuel_needed_destination
    where id = ip_id and tag = ip_tag;
    
    update drivers
    set successful_trips = successful_trips + 1
    where username = (select driven_by from vans where id = ip_id and tag = ip_tag);
end //
delimiter ;

-- [18] purchase_product()
-- -----------------------------------------------------------------------------
/* This stored procedure allows a business to purchase products from a van
at its current location.  The van must have the desired quantity of the product
being purchased.  And the business must have enough money to purchase the
products.  If the transaction is otherwise valid, then the van and business
information must be changed appropriately.  Finally, we need to ensure that all
quantities in the payload table (post transaction) are greater than zero. */
-- -----------------------------------------------------------------------------
drop procedure if exists purchase_product;
delimiter //
create procedure purchase_product (in ip_long_name varchar(40), in ip_id varchar(40),
	in ip_tag integer, in ip_barcode varchar(40), in ip_quantity integer)
sp_main: begin
	-- ensure that the business is valid
    if (select count(*) from businesses where long_name = ip_long_name) = 0 then
		leave sp_main;
	end if;
    -- ensure that the van is valid and exists at the business's location
    if (select count(*) from vans where (id = ip_id and tag = ip_tag and located_at = (select location from businesses where long_name = ip_long_name))) = 0 then
		leave sp_main;
	end if;
	-- ensure that the van has enough of the requested product
    if (select quantity from contain where (id = ip_id and tag = ip_tag and barcode = ip_barcode)) < ip_quantity or 
    (select count(*) from contain where (id = ip_id and tag = ip_tag and barcode = ip_barcode)) < 1 then
		leave sp_main;
	end if;
	-- update the van's payload
    update contain
    set quantity = quantity - ip_quantity
    where id = ip_id and tag = ip_tag and barcode = ip_barcode;
    -- update the monies spent and gained for the van and business
    update vans
    set sales = sales + ((select price from contain where (id = ip_id and tag = ip_tag and barcode = ip_barcode)) * ip_quantity)
    where id = ip_id and tag = ip_tag;
    
    update businesses
    set spent = spent + ((select price from contain where (id = ip_id and tag = ip_tag and barcode = ip_barcode)) * ip_quantity)
    where long_name = ip_long_name;
    
    -- ensure all quantities in the payload table are greater than zero
    delete from contain where quantity <= 0;
end //
delimiter ;

-- [19] remove_product()
-- -----------------------------------------------------------------------------
/* This stored procedure removes an product from the system.  The removal can
occur if, and only if, the product is not being carried by any vans. */
-- -----------------------------------------------------------------------------
drop procedure if exists remove_product;
delimiter //
create procedure remove_product (in ip_barcode varchar(40))
sp_main: begin
	-- ensure that the product exists
    if (select count(*) from products where barcode = ip_barcode) = 0 then
		leave sp_main;
	end if;
    -- ensure that the product is not being carried by any vans
    if (select count(*) from contain where barcode = ip_barcode) > 0 then
		leave sp_main;
	end if;
    
    delete from products
    where barcode = ip_barcode;
    
end //
delimiter ;

-- [20] remove_van()
-- -----------------------------------------------------------------------------
/* This stored procedure removes a van from the system.  The removal can
occur if, and only if, the van is not carrying any products.*/
-- -----------------------------------------------------------------------------
drop procedure if exists remove_van;
delimiter //
create procedure remove_van (in ip_id varchar(40), in ip_tag integer)
sp_main: begin
	-- ensure that the van exists
    if (select count(*) from vans where id = ip_id and tag = ip_tag) = 0 then
		leave sp_main;
	end if;
    -- ensure that the van is not carrying any products
    if (select count(*) from contain where id = ip_id and tag = ip_tag) > 0 then
		leave sp_main;
	end if;
    
    delete from vans
    where id = ip_id and tag = ip_tag;
end //
delimiter ;

-- [21] remove_driver_role()
-- -----------------------------------------------------------------------------
/* This stored procedure removes a driver from the system.  The removal can
occur if, and only if, the driver is not controlling any vans.  Also, if the
driver also has a worker role, then the worker information must be maintained;
otherwise, the driver's information must be completely removed from the system. */
-- -----------------------------------------------------------------------------
drop procedure if exists remove_driver_role;
delimiter //
create procedure remove_driver_role (in ip_username varchar(40))
sp_main: begin
	-- ensure that the driver exists
    if (select count(*) from drivers where username = ip_username) = 0 then
		 leave sp_main;
	end if;
    -- ensure that the driver is not controlling any vans
    if (select count(*) from vans where driven_by = ip_username) > 0 then 
		leave sp_main;
	end if;
    -- remove all remaining information unless the driver is also a worker
    if (select count(*) from workers where username = ip_username) > 0 then
		delete from drivers
		where username = ip_username;
	else
		delete from drivers
        where username = ip_username;

        delete from users
        where username = ip_username;
        
        delete from employees
        where username = ip_username;
	end if;
end //
delimiter ;

-- [22] display_owner_view()
-- -----------------------------------------------------------------------------
/* This view displays information in the system from the perspective of an owner.
For each owner, it includes the owner's information, along with the number of
businesses for which they provide funds and the number of different places where
those businesses are located.  It also includes the highest and lowest ratings
for each of those businesses, as well as the total amount of debt based on the
monies spent purchasing products by all of those businesses. And if an owner
doesn't fund any businesses then display zeros for the highs, lows and debt. */
-- -----------------------------------------------------------------------------
create or replace view display_owner_view as
select business_owners.username, users.first_name, users.last_name, users.address, count(fund.business) AS num_businesses, count(distinct businesses.location) AS num_places, IFNULL(MAX(businesses.rating), 0) AS highs,
IFNULL(MIN(businesses.rating), 0) AS lows, IFNULL(SUM(businesses.spent), 0) AS debt
from business_owners
left join fund on fund.username = business_owners.username
left join businesses on businesses.long_name = fund.business
join users on business_owners.username = users.username
group by business_owners.username;

-- [23] display_employee_view()
-- -----------------------------------------------------------------------------
/* This view displays information in the system from the perspective of an employee.
For each employee, it includes the username, tax identifier, hiring date and
experience level, along with the license identifer and drivering experience (if
applicable), and a 'yes' or 'no' depending on the manager status of the employee. */
-- -----------------------------------------------------------------------------
create or replace view display_employee_view as
select distinct employees.username as username, employees.taxID as taxID, employees.salary as salary, employees.hired as hired, employees.experience as employee_experience, IFNULL(drivers.licenseID, 'n/a') as licenseID, IFNULL(drivers.successful_trips, 'n/a') as driving_experience,
IF(employees.username = delivery_services.manager, 'yes', 'no') as manager_status
from employees
left join drivers on employees.username = drivers.username
left join delivery_services on employees.username = delivery_services.manager;

-- [24] display_driver_view()
-- -----------------------------------------------------------------------------
/* This view displays information in the system from the perspective of a driver.
For each driver, it includes the username, licenseID and drivering experience, along
with the number of vans that they are controlling. */
-- -----------------------------------------------------------------------------
create or replace view display_driver_view as
select drivers.username, drivers.licenseID, drivers.successful_trips, count(vans.id)
from drivers
left join vans on vans.driven_by = drivers.username
group by drivers.username;


-- [25] display_location_view()
-- -----------------------------------------------------------------------------
/* This view displays information in the system from the perspective of a location.
For each location, it includes the label, x- and y- coordinates, along with the
name of the business or service at that location, the number of vans as well as 
the identifiers of the vans at the location (sorted by the tag), and both the 
total and remaining capacity at the location. */
-- -----------------------------------------------------------------------------
create or replace view display_location_view as
select locations.label, businesses.long_name, locations.x_coord, locations.y_coord, locations.space, COUNT(vans.id) as num_vans, 
GROUP_CONCAT(CONCAT(vans.id, vans.tag) order by vans.tag) as van_ids, 
(locations.space - COUNT(vans.id)) as remaining_capacity
from locations
join businesses on locations.label = businesses.location
join vans on vans.located_at = locations.label
group by locations.label, locations.x_coord, locations.y_coord, businesses.long_name, locations.space
union
select locations.label, delivery_services.long_name,
locations.x_coord, locations.y_coord, locations.space,COUNT(vans.id) as num_vans, 
GROUP_CONCAT(CONCAT(vans.id, vans.tag) order by vans.tag) as van_ids, 
(locations.space - COUNT(vans.id)) as remaining_capacity
from locations
join delivery_services on delivery_services.home_base = locations.label
join vans on vans.located_at = locations.label
group by locations.label, locations.x_coord, locations.y_coord, delivery_services.long_name, locations.space;

-- [26] display_product_view()
-- -----------------------------------------------------------------------------
/* This view displays information in the system from the perspective of the products.
For each product that is being carried by at least one van, it includes a list of
the various locations where it can be purchased, along with the total number of packages
that can be purchased and the lowest and highest prices at which the product is being
sold at that location. */
-- -----------------------------------------------------------------------------
create or replace view display_product_view as
select p.iname, v.located_at, sum(c.quantity), min(c.price), max(c.price) 
from products as p 
join contain as c on p.barcode = c.barcode 
join vans as v on concat(c.id, c.tag) = concat(v.id, v.tag)
group by v.located_at, p.barcode
order by p.iname;

-- [27] display_service_view()
-- -----------------------------------------------------------------------------
/* This view displays information in the system from the perspective of a delivery
service.  It includes the identifier, name, home base location and manager for the
service, along with the total sales from the vans.  It must also include the number
of unique products along with the total cost and weight of those products being
carried by the vans. */
-- -----------------------------------------------------------------------------
create or replace view display_service_view as
select ds.id, ds.long_name, ds.home_base, ds.manager, 
coalesce((select sum(sales) from vans where id = ds.id), 0) as revenue, 
count(distinct c.barcode) as products_carried, 
    case 
        when sum(c.price * c.quantity) is null or sum(c.price * c.quantity) = 0 then null
        else sum(c.price * c.quantity)
    end as cost_carried, 
    case 
        when sum(c.quantity * p.weight) is null or sum(c.quantity * p.weight) = 0 then null
        else sum(c.quantity * p.weight)
    end as weight_carried
from delivery_services ds
left join vans v on ds.id = v.id
left join contain c on c.id = v.id and c.tag = v.tag
left join products p on c.barcode = p.barcode
group by ds.id, ds.long_name, ds.home_base, ds.manager;


