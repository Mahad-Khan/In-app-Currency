# dirname = os.path.dirname(os.path.abspath(__file__))
# dirname_list = dirname.split("/")[:-1]
# dirname = "/".join(dirname_list)
# path = dirname + "/api"
# sys.path.append(path)

from blue import app



if __name__ == "__main__":
    app.run(host="0.0.0.0")
