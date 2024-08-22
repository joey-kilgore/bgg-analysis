
def writeHeaderHTMLTable(filePath, tableName):
    htmlHeader = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Game Ownership Lists</title>
            <link rel="stylesheet" href="_static/styles.css">
        </head>
        <body>
        '''
        
    htmlHeader+=f'''\n<input type="text" id="{tableName+"_search_bar"}" onkeyup="searchTable('{tableName+"_search_bar"}', '{tableName}')" placeholder="Search for usernames or game names..">'''
    htmlHeader+=f'\n <table id="{tableName}">'

    with open(filePath,'w') as f:
        f.write(htmlHeader)

def writeFooterHTMLTable(filePath):
    htmlFooter = '''
    </table>
    
    <script src="_static/search.js"></script>
    
    </body>
    </html>
    '''
    with open(filePath,'a') as f:
        f.write(htmlFooter)
