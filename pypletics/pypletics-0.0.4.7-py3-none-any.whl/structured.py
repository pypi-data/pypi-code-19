#!/usr/bin/env python
# -*- coding: utf-8 -*-

def F_manage_MultiAddressees(text, sep):
    if sep in text:
        return 1
    return 0


def get_structured_df(df_target, column_name_tomanage, separator, column_final):
    '''
    This function allows us to structured our dataframe. For example, if we have severals addressees in a same column, 1 will be keep in a row and the others will be in new rows, just below with the same values in each other column because we want to keep the sender, the subjetc etc.
    '''
    #temp column
    df_target["Addressee_Copy"] = df_target[column_name_tomanage]
    copy_name = "Addressee_Copy"
    
    df_target["_has_separator"] = df_target["Addressee_Copy"].apply(F_manage_MultiAddressees, sep=separator)
    
    df_structured = (df_target
     .set_index(df_target.columns.drop(copy_name, 1).tolist())
     .Addressee_Copy
     .str.split(separator, expand=True)
     .stack()
     .reset_index()
     .rename(columns={0:column_final}))
    
    id_column_final = str("ID_" + column_final)
    df_structured.columns.values[len(df_structured.columns)-2] = id_column_final
    df_structured[id_column_final] = df_structured["_has_separator"] + df_structured[id_column_final]
    del df_structured["_has_separator"]
    
    return df_structured




if __name__ == '__main__':
    #introduction()
    print("Bonjour")