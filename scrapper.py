from cryptography import fernet
from selenium import webdriver
from cryptography.fernet import Fernet
import time
import re

def get_original_text(target_exam_page, output_file_name, numer_of_question):
    driver = webdriver.Chrome("your PATH TO CHROME DRIVER")
    # decrypt my pw and id(*** do not print my id and password *** )
    key = b'UPlNgbpm_lK8oismh6e6c4PDmT4w1h4g6tMDUqtcKSU='
    user_id_encrypt = b'gAAAAABgsfAE-NeQLmGkiCFHh6ZET0KFBLHBRWadIK0zs6pI7PvMIGyi4FGC5WggmDes_ZRzdh_rRn74yQc8M3XstPsz1vK38w=='
    user_pw_encrypt = b'gAAAAABgsfAX2-z3eiQ_x2T1kIpA6N4fRC1nI225_MLoeOxjNe9RJC2CJ_ZdK7lLwno27Fp5LUFB8Dn4hSZklq3L5cid1qM7OQ=='
    fernet = Fernet(key)
    user_id = fernet.decrypt(user_id_encrypt).decode()
    user_pw = fernet.decrypt(user_pw_encrypt).decode()
    # print(user_id)
    # print(user_pw)
    ebsi_home_page = "https://www.ebsi.co.kr/ebs/pot/potl/login.ebs?destination=/ebs/pot/poti/main.ebs&alertYn=N"

    output_file = open(output_file_name, "w", encoding="utf-8")
    driver.get(ebsi_home_page)
    time.sleep(1)
    id_input = driver.find_element_by_xpath('//*[@id="loginFrm"]/input[11]')
    id_input.send_keys(user_id)
    pw_input = driver.find_element_by_xpath('//*[@id="loginFrm"]/span/input')
    pw_input.send_keys(user_pw)
    login_button = driver.find_element_by_xpath('//*[@id="btnLogin"]')
    login_button.click()
    time.sleep(2)
    driver.get(target_exam_page)
    time.sleep(5)
    for i in range(numer_of_question):

        next_button = driver.find_element_by_id("oneItemNextPaging")
        # 문제의 text는 divQuestion > divParagraph 안에있는 span태그에 들어있다.
        # 하지만 원하는 element말고 다른 element들도 같이 딸려옴
        # 우리가 원하는 element는 id를 사용하지 않아 매우 번거롭게도 filtering을 해줘야 한다
        paragraph = driver.find_elements_by_css_selector("[name=divQuestion]>[name=divParagraph]")
        print(len(paragraph))
        to_write = "" # file에 작성할 문제 string
        for p in paragraph:
          
            paragraph_span = p.find_elements_by_tag_name("span")
            # 문제와 선지 사이에 단어들의 뜻을 *car : 자동차 이런식으로 써놓은 것들이 있는데
            # 이것들도 걸러준다
            if "*" in p.text:
                print(p.text)
                continue
            for s in paragraph_span:
                # element들중에서 text-decoration : underline 의 css property를 가진 element가 
                # 있는데, 빈칸문제에서 빈칸에 해당하는 부분이다.
                # 그냥 넘어가면 나중에 답을 빈칸에 채울때  빈칸이 뚫린 위치를 모르기때문에
                # ____로 replace해준다
                if "underline" in s.value_of_css_property("text-decoration"):
                    to_write += "____"
                if (re.search(r"[a-z]|_", s.text) == None and s.text != ".") or re.search(r"\*.+:", s.text) != None:
                    continue
                # print(s.text.strip())
                to_write += s.text.strip()
        # to write이 비어잇는 경우는 위에서 처리한 문제 형식과 다른 형식으로 html코드가 짜여잇는 경우다.
        
        if to_write == "":
            paragraph = driver.find_elements_by_css_selector('[name="divTableCell"] [name="divParagraph"]')
            for p in paragraph:
          
                paragraph_span = p.find_elements_by_tag_name("span")
                if "*" in p.text: # 단어 정의 걸러주는 부분
                    print(p.text)
                    continue
                for s in paragraph_span:
                    if "underline" in s.value_of_css_property("text-decoration"):
                        to_write += "____"
                    if re.search(r"[a-z]|_", s.text) == None or re.search(r"\*.+:", s.text) != None:
                        continue
                    to_write += s.text.strip()
        # 선지 element마다 iscorrectanswer property를 가지고 있는데 답에만
        # True속성을 갖게 되어있고 나머지는 False이다 
        ans_li = driver.find_element_by_css_selector('[iscorrectanswer="True"]')
        ans = " "+ans_li.find_element_by_tag_name("span").text
        # 빈칸을 찾아서 답을 작성해 준다
        to_write = re.sub(r'_+',ans, to_write)
        if len(to_write) <= 10:
            continue
        output_file.write(to_write)
        next_button.click()
        output_file.write("\n")
        time.sleep(1)
    output_file.close()
if __name__ == "__main__":
    grammer_100_exam = "https://www.ebsi.co.kr/ebs/xip/xipSolve/itempool.ebs?IsMoc=False&FrontType=Paper&ParameterType=Normal&ID=21192080&myQboxYN=Y&bd=%25EB%25AC%25B8%25EB%25B2%2595%2520%25EB%258F%2599%25EC%2582%25AC%2520%25EC%259C%2584%25EC%25A3%25BC%2520100&site=HSC&openerAction=refresh&openerActionCondition="
    blank_100_exam  = "https://www.ebsi.co.kr/ebs/xip/xipSolve/itempool.ebs?IsMoc=False&FrontType=Paper&ParameterType=Normal&ID=21191742&myQboxYN=Y&bd=%25EC%2598%2581%25EC%2596%25B4%2520%25EB%25B9%2588%25EC%25B9%25B8%25EC%25B6%2594%25EB%25A1%25A0%2520100%25EC%25A0%259C%25201&site=HSC&openerAction=refresh&openerActionCondition="

    get_original_text(target_exam_page=blank_100_exam, output_file_name="빈칸100.txt", numer_of_question=10)