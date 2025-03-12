import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Sesuaikan path chromedriver jika diperlukan
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
BASE_URL = "http://localhost/workspaces/DamnCRUD-UAS"

class IntegrationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome(service=ChromeService(executable_path=CHROMEDRIVER_PATH))
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def login(self, username, password):
        # Buka halaman login
        self.driver.get(f"{BASE_URL}/login.php")
        # Asumsikan field login memiliki name "username" dan "password"
        username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = self.driver.find_element(By.NAME, "password")
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        # Klik tombol login (asumsikan tombol login bertipe "submit")
        login_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
        login_button.click()

    def test_valid_login(self):
        """Test Case 1"""
        self.login("admin", "nimda666!")
        # Tunggu sampai halaman dashboard index.php termuat
        self.wait.until(EC.url_contains("index.php"))
        self.assertIn("Dashboard", self.driver.page_source)
        time.sleep(1)

    def test_invalid_login(self):
        """Test Case 2"""
        self.driver.get(f"{BASE_URL}/login.php")
        username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = self.driver.find_element(By.NAME, "password")
        username_field.clear()
        username_field.send_keys("wronguser")
        password_field.clear()
        password_field.send_keys("wrongpass")
        login_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
        login_button.click()
        # Tunggu error message muncul
        error_message = self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'wrong credentials')]")))
        self.assertTrue(error_message.is_displayed())
        time.sleep(1)

    def test_create_contact(self):
        """Test Case 3"""
        self.login("admin", "nimda666!")
        # Asumsikan ada link atau tombol untuk ke create.php
        self.wait.until(EC.url_contains("index.php"))
        self.driver.get(f"{BASE_URL}/create.php")
        # Isi form kontak (sesuaikan name field sesuai implementasi)
        name_field = self.wait.until(EC.presence_of_element_located((By.NAME, "name")))
        email_field = self.driver.find_element(By.NAME, "email")
        phone_field = self.driver.find_element(By.NAME, "phone")
        title_field = self.driver.find_element(By.NAME, "title")
        name_field.send_keys("Test Contact")
        email_field.send_keys("test@example.com")
        phone_field.send_keys("1234567890")
        title_field.send_keys("Tester")
        # Submit form
        submit_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
        submit_button.click()
        # Verifikasi bahwa data kontak muncul di dashboard
        self.wait.until(EC.url_contains("index.php"))
        self.assertIn("Test Contact", self.driver.page_source)
        time.sleep(1)

    def test_update_contact(self):
        """Test Case 4"""
        self.login("admin", "nimda666!")
        # Arahkan ke halaman update.php dengan id kontak, misal id=1
        self.driver.get(f"{BASE_URL}/update.php?id=1")
        # Asumsikan form update memiliki field name "name"
        name_field = self.wait.until(EC.presence_of_element_located((By.NAME, "name")))
        name_field.clear()
        name_field.send_keys("Updated Contact")
        submit_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
        submit_button.click()
        # Verifikasi bahwa halaman dashboard menampilkan kontak yang telah diperbarui
        self.wait.until(EC.url_contains("index.php"))
        self.assertIn("Updated Contact", self.driver.page_source)
        time.sleep(1)

    def test_xss_detection(self):
        """Test Case 5"""
        self.login("admin", "nimda666!")
        # Arahkan ke halaman vpage.php
        self.driver.get(f"{BASE_URL}/vpage.php")
        # Isikan payload XSS pada form, asumsikan field bernama "thing"
        thing_field = self.wait.until(EC.presence_of_element_located((By.NAME, "thing")))
        xss_payload = '<script>alert("xss")</script>'
        thing_field.clear()
        thing_field.send_keys(xss_payload)
        submit_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
        submit_button.click()
        # Tunggu sampai data muncul, cek apakah nilai input tampil (tidak dieksekusi)
        content = self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Your thing is')]")))
        self.assertIn(xss_payload, content.text)
        # Untuk mencegah terjadinya alert, selenium otomatis akan menolak dialog alert.
        time.sleep(1)

if __name__ == "__main__":
    unittest.main()