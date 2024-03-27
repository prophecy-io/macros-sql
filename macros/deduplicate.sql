{%- macro deduplicate(relation, partition_by, order_by) -%}

    with row_numbered as (
        select
            _inner.*,
            row_number() over (
                partition by {{ partition_by }}
                order by {{ order_by }}
            ) as rn
        from {{ relation }} as _inner
    )
    select
            distinct data.*
    from {{ relation }} as data
    natural join row_numbered
    where row_numbered.rn = 1
{%- endmacro -%}

{%- macro deduplicate_simple(relation) -%}
    select
        distinct * from {{relation}}
{%- endmacro -%}