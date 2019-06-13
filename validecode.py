# -*- coding: utf-8 -*-

import random
from captcha.image import ImageCaptcha  # 验证码库
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt


code_char_set = ['0','1','2','3','4','5','6','7','8','9',
                'q','w','e','r','t','y','u','i','o','p',
                'a','s','d','f','g','h','j','k','l','z',
                'x','c','v','b','n','m','Q','W','E','R',
                 'T','Y','U','I','O','P','A','S','D','F',
                'G','H','J','K','L','Z','X','C','V','B','N','M']

def random_code_text(code_size=4):
  '''
  随机产生验证码字符
  '''
  code_text = []
  for i in range(code_size):
    c = random.choice(code_char_set)
    code_text.append(c)
  return code_text

def generate_code_image(code_size):
  image = ImageCaptcha()
  code_text = random_code_text(code_size)
  code_text = ''.join(code_text)
  # 将字符串转换成验证码
  captcha = image.generate(code_text)
  # 保存验证码
  image.write(code_text, code_text+'.jpg')
  
  # 将验证码转换成图片
  code_image = Image.open(captcha)
  code_image = np.array(code_image)
  return code_text, code_image

if __name__ == '__main__':
  text, image = generate_code_image(4)
  ax = plt.figure()
  ax.text(0.1,0.9,text, ha='center', va='center')
  plt.imshow(image)
  plt.show()