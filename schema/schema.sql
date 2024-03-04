CREATE TABLE task_list(  
    id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    statusTask BOOLEAN,
    closeAt TIMESTAMP,
    shiftTasks VARCHAR(255),
    lice VARCHAR(255),
    shift VARCHAR(255),
    brigade VARCHAR(255),
    batchNum INT,
    batchDate DATE,
    nomenclat VARCHAR(255),
    codeEKN VARCHAR(255),
    idRC VARCHAR(255),
    dateStart timestamp ,
    dateEnd timestamp 
);