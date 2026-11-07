
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id
from `clear-nebula-510706-t0`.`CareFlow_data_CareFlow_Data`.`my_second_dbt_model`
where id is null



  
  
      
    ) dbt_internal_test