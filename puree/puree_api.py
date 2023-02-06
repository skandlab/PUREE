from cProfile import run
import requests
import time
import os
import pandas as pd
BASE_URL = 'https://puree.genome.sg/server'

TEMP_FILE_DIR = r'tmp_dir'
if not os.path.exists(TEMP_FILE_DIR):
    os.makedirs(TEMP_FILE_DIR)

class PUREE:
    
    def __init__(self):
        pass
    
    def monitor(self):
        """
        Monitor the health of the backend.
        Returns:
            True: If the server is running successfully.
            False: If there is an error with the server.
        """

        monitor_url = BASE_URL + '/monitor'
        response = requests.get(monitor_url)
        if response.status_code != 200:
            return False
        if response.text != 'Server running successfully':
            return False
        return True

    def check_and_correct_file(self, file_path, verbose=True):
        """
        Check and correct the given file if necessary.
        Args:
            file_path: path to the file to be processed.
            verbose: If set to True, will print any relevant messages.
        Returns:
            The corrected file path.
        """

        if not (file_path.endswith(".tsv") or file_path.endswith('.csv') or file_path.endswith(".txt")):
            return False
        if file_path.endswith(".tsv") or file_path.endswith(".txt"):
            df = pd.read_csv(file_path, sep='\t')
        else:
            df = pd.read_csv(file_path)
        cols = df.columns.tolist()
        if len(cols) < len(df):
            for i in cols[1:]:
                if not (i.startswith("sample") or i.startswith("Sample")):
                    df.columns = [cols[0]]+[f'Sample_{i}' for i in range(1, len(cols))]
                    df.to_csv(os.path.join(TEMP_FILE_DIR, file_path[:-4]+'.tsv'), sep='\t', index=False)
                    if verbose:
                        print("Sample names were not encrypted... Encryption is completed.")
                    return os.path.join(TEMP_FILE_DIR, file_path[:-4]+".tsv")
        else:
            sample_names = df[cols[0]].tolist()
            for i in sample_names:
                if not (i.startswith("sample") or i.startswith("Sample")):
                    df[cols[0]] = [f'Sample_{i}' for i in range(1, len(df)+1)]
                    df.to_csv(os.path.join(TEMP_FILE_DIR, file_path[:-4]+'.tsv'), sep='\t', index=False)
                    if verbose:
                        print("Sample names were not encrypted... Encryption is completed.")
                    return os.path.join(TEMP_FILE_DIR, file_path[:-4]+".tsv")
        if file_path.endswith(".csv") or file_path.endswith(".txt"):
            df.to_csv(os.path.join(TEMP_FILE_DIR, file_path[:-4]+'.tsv'), sep='\t', index=False)
            return os.path.join(TEMP_FILE_DIR, file_path[:-4]+".tsv")
        else:
            return file_path

    def submit_file(self, file_path, email_id, gene_identifier_type='ENSEMBL'):

        """
        Submit a file for PUREE processing.
        Args:
            file_path: path to the file to be processed.
            gene_identifier_type: type of gene identifier used in the file. Can be ENSEMBL/HGNC (defaults to ENSEMBL).
        Returns:
            A tuple with the following information:
            success: Boolean indicating if the file was submitted successfully or not.
            message: String message with additional information.
        Sample Outputs:
            File submitted for processing successfully
                {'id': '781ed18b-5754-4b03-b9cf-4c8049792a75', 'success': True}
            File submission failed
                {'id': '781ed18b-5754-4b03-b9cf-4c8049792a75', 'success': False}
        """

        try:
            if not (file_path.endswith(".tsv") or file_path.endswith('.csv') or file_path.endswith(".txt")):
                return False, "Not a compatible file. Please upload .txt/.tsv/.csv file"
            final_file_path = self.check_and_correct_file(file_path)
            if not final_file_path:
                return False, "Check the file type"
            submit_url = BASE_URL + '/main'
            data = {'gene_identifier_type': gene_identifier_type, 'run_mode': 'PUREE_genes', 'email_id': email_id, "file_name": os.path.basename(file_path)}
            files = {'file': open(final_file_path, 'r')}
            response = requests.post(submit_url, files=files, data=data)
            return response, None
        except Exception as e:
            return False, e

    def puree_output(self, id):

        """
        Get the processed output from PUREE.
        
        Parameters:
            id (int): The ID of the processed file.
        
        Returns:
            text output if successful OR
            dict: {'success': 'False', 'message': Reason for False Success}
                if the request fails.
        
        Raises:
            None
        """

        file_url = BASE_URL + '/get_file?id={}'
        c = 0
        while c<200:
            try:
                response = requests.get(file_url.format(id))
                response.json()
                time.sleep(10)
                c+=10
            except:
                return response
        return False

    def get_logs(self, id):
        '''
        Get the logs from PUREE
        Outputs:
            text output OR
            {'success': 'False', 'message': Reason for False Success}
        '''
        try:
            logs_url = BASE_URL + '/get_logs?id={}'
            response = requests.get(logs_url.format(id))
            return response
        except:
            return False

    def process_output(self, str):
        """
        Processes the input text and returns a Pandas DataFrame.

        Parameters:
        t (str) : The input text to be processed.

        Returns:
        Pandas DataFrame : The processed output in a tabular format.

        Example:
        >>> process_output("col1\\tcol2\\nval1\\tval2")
        """
        str = 'sample_name'+str
        str = str.split('\n')
        str = list(map(lambda x: x.split('\t'), str))
        str = str[:-1]
        d = pd.DataFrame(str[1:], columns=str[0])
        return d

    def get_output(self, file_path, gene_identifier_type, email_id, verbose=True):
        """
        Get the processed output and logs for a given file.
        
        Arguments:
            file_path (str): Path to the input file.
            gene_identifier_type (str): Type of gene identifier used in the input file.
            verbose (bool, optional): If set to True, the logs for the file processing will be printed. Defaults to True.
            
        Returns:
            dict or tuple: A dictionary containing processed output and logs OR a tuple with False and error message.
            The dictionary has two keys:
                'output': A pandas dataframe containing processed output from file.
                'logs': Logs for the file processing in text format.
            
        In case of an error, a tuple with False and error message is returned.
        """
        file_output = self.submit_file(file_path, email_id, gene_identifier_type=gene_identifier_type)
        if file_output[1] is not None:
            return False, file_output[1]
        else:
            id = file_output[0].json()['id']
            processed_output = self.puree_output(id)
            if processed_output:
                logs_output = self.get_logs(id)
                if verbose:
                    print(f"**********LOGS FOR {file_path}**********")
                    print(logs_output.text)
                return {"output": self.process_output(processed_output.text), 'logs':logs_output.text}
        return False, "Error"