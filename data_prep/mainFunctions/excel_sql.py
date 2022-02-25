import pandas as pd

## ## ## ## ## ----- SAVE DATAFRAME TO EXCEL FILE  ----- ## ## ## ## ##
def dfTOxls(dest_path, fileName, frame):
    # Create a Pandas Excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter(dest_path + "/{}.xlsx".format(fileName),  index = False, header=True)
    # Convert the dataframe to an XlsxWriter Excel object.
    frame.to_excel(writer, sheet_name='Sheet1')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

## ## ## ## ## ----- CREATE QUERY IN PROSTGRES AND EXPORT TO EXCEL  ----- ## ## ## ## ##
def sqlTOxls(engine,query,dest_path, fileName):
    #query = 'SELECT * FROM unsd'
    df = pd.read_sql_query(query,con=engine)
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(dest_path + "/{}.xlsx".format(fileName), index = False, header=True)
    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name='Sheet1')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()