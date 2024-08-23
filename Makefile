app:
	docker build -t wpop-presales-demo-login-image .

run:
	docker run -d --name wpop-presales-demo-login -p 8089:8089 wpop-presales-demo-login-image