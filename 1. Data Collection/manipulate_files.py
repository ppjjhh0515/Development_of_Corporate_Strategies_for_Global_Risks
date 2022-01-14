import os
import shutil


def aggregate_files(doc_type="10-K", save_path="./data", overwrite=False):
	
	years = ["19", "20", "21"]

	filings_folder = "./sec-edgar-filings"
	sub_dirs = os.listdir(filings_folder)
	save_path = os.path.join(save_path, doc_type)

	# check if save path exists, otherwise create a new folder
	if not os.path.exists(save_path):
		os.mkdir(save_path)

	# check if save path for each year exists, otherwise create a new folder for it
	for year in years:
		dest_dir = os.path.join(save_path, year)
		if not os.path.exists(dest_dir):
			os.mkdir(dest_dir)

	# for each cik, copy desired files to save_path
	for cik in sub_dirs:
		
		if cik.startswith("."):
			continue

		dest = os.path.join(filings_folder, cik, doc_type)

		try:
			for folder_path in os.listdir(dest):
				if folder_path.startswith("."):
					continue

				# the second element indicates the year
				y = folder_path.split('-')[1]


				if y in years and not overwrite and not os.path.exists(os.path.join(save_path, y, cik, folder_path)):
					shutil.copytree(os.path.join(dest, folder_path), os.path.join(save_path, y, cik, folder_path))
					print("transferred ", os.path.join(dest, folder_path))
				elif y in years and overwrite:
					shutil.copytree(os.path.join(dest, folder_path), os.path.join(save_path, y, cik, folder_path))
					print("transferred ", os.path.join(dest, folder_path))

		except Exception as e:
			print(e)


def delete_filings_txt(doc_type="10-K", filings_folder="./sec-edgar-filings"):

	# list out all existing ciks in given folder
	sub_dirs = os.listdir(filings_folder)

	# process files of each cik
	for cik in sub_dirs:

		# ignore the folder with leading dot
		if cik.startswith("."):
			continue

		# create the valid path of the cik
		dest = os.path.join(filings_folder, cik, doc_type)
		
		# list out all existing filings, but the cik might not have given doc_type, 
		# so used try/execpt to avoid error
		try:
			for folder_path in os.listdir(dest):
				try:
					# generate the path of the file to be deleted
					target = os.path.join(dest, folder_path, "full-submission.txt")
					os.remove(target)
					print("Deleted ", target)

				except Exception as e:
					print(e)
		except Exception as e:
			print(e)


if __name__ == "__main__":
	delete_filings_txt(doc_type="10-Q")
	aggregate_files(doc_type="10-Q")


