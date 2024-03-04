CREATE TABLE task_list(  
    id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    status_task BOOLEAN,
    close_at TIMESTAMP,
    shift_tasks VARCHAR(255),
    lice VARCHAR(255),
    shift VARCHAR(255),
    brigade VARCHAR(255),
    batch_num INT,
    batch_date DATE,
    nomenclat VARCHAR(255),
    code_ekn VARCHAR(255),
    id_rc VARCHAR(255),
    date_start timestamp ,
    date_end timestamp 
);

CREATE TABLE product_list(
    id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_roduct VARCHAR(255),
    lot_id INT,
    lot_data TIMESTAMP,
    is_aggregated BOOLEAN,
    aggregated_at TIMESTAMP
)