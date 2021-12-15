/* ----------------------------------------------------------------------
#
# File: RQHardswish.c
#
# Last edited: 23.02.2024
#
# Copyright (C) 2024, ETH Zurich and University of Bologna.
#
# Author:
# - Victor Jung, jungvi@iis.ee.ethz.ch, ETH Zurich
#
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the License); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
*/

#include "DeeployBasicMath.h"

void RQiHardswish_s8_s8(int8_t *input, int8_t *output, int32_t size,
                        int32_t one_over_six, int32_t three, int32_t six,
                        int32_t input_offset, int32_t output_offset,
                        int32_t mul, int32_t add, int32_t shift) {

  int32_t temp;

  for (int i = 0; i < size; i++) {
    temp = input[i] + input_offset + three;
    if (temp < 0) {
      temp = 0;
    }
    if (temp > six) {
      temp = six;
    }
    temp = temp * one_over_six;
    temp = input[i] * temp;
    temp = temp * (mul) + (add);
    temp = ((temp + ((1 << ((shift)-1)))) >> (shift)) + output_offset;
    output[i] = (int8_t)CLAMP(temp, -128, 127);
  }
}