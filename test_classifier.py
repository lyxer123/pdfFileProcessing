import os
import sys
from pdf_standard_classifier import classify_pdf, CATEGORIES

def test_specific_files():
    """测试特定文件的分类结果"""
    
    # 测试文件列表（您提到的文件）
    test_files = [
        # 原有测试文件
        "ESP32-DevKit-Lipo_Rev_A1.pdf",  # 应该是电路图
        "34 C191602_2.2MH@1KHZ3A_2018-05-02.PDF",  # 应该是规格书
        "1N4148WS_Diotec_Semiconductor.pdf",  # 应该是规格书
        "WizFi360io_H_SCH_V100.pdf",  # 应该是电路图
        "充电桩的采集与监控系统和充电桩.pdf",  # 应该是专利
        "充电模块升级技术要求及调研需求2022-5-15.pdf",  # 应该是技术文档
        "单相电表模块ATT7053AU使用说明书1.1.pdf",  # 应该是说明书
        "永联科技回复.pdf",  # 应该是其他
        "海汇德160KW电气原理图纸V1.03.pdf",  # 应该是图纸
        "红外读头.pdf",  # 应该是说明书
        "苏创自研控制器项目计划.pdf",  # 应该是技术文档
        "附件2：应聘登记表.pdf",  # 应该是其他
        
        # 新增测试文件
        "1_固德威并网MTG2SMTSDTG2MSDNSXS系列逆变器Modbus通信协议-客户版.pdf",  # 应该是设备通讯协议
        "1_固德威并网MTG2SMTSDTG2MSDNSXS系列逆变器Modbus通信协议（正泰是smt）.pdf",  # 应该是设备通讯协议
        "1-2 Blue Pill STM32 con LDmicro.pdf",  # 应该是说明书
        "4 C2922458_等级_X1,Y24.7NF±10%250VAC_2022-07-26.PDF",  # 应该是元器件说明书
        "4-台区智能融合终端功能模块型式规范-征求意见稿.pdf",  # 应该是企业标准
        "6.2《大规模电动汽车安全充放电与车-网智能互动关键技术》科学技术项目合同.pdf",  # 应该是合同
        "6.78 MHz Wireless Power Transfer with Self Resonant Coils at 95 percent DC-DC Efficiency.pdf",  # 应该是论文
        "7-功率分析仪.pdf",  # 应该是技术文档
        "08-29-19 PCCC Documentation.pdf",  # 应该是技术文档
        "8.1 科学技术项目合同（2023版）-20231117V2.pdf",  # 应该是合同
        "8BG000-A7680C-TE_V3.01_DL(230831).pdf",  # 应该是图纸
        "11-2.高比例可再生能源接入下考虑运行灵活性的电力系统规划研究-论文1-国网滨州供电公司.pdf",  # 应该是论文
        "49 C423021_6.8KΩ±0.5%100MW_2020-03-06.PDF",  # 应该是元器件说明书
        "55 C2989257_20KΩ±0.5%100MW_2022-07-08.PDF",  # 应该是元器件说明书
        "63 C23186_5.1KΩ±1%100MW_2020-03-06.PDF",  # 应该是元器件说明书
        "64 C23162_4.7KΩ±1%100MW_2020-03-06.PDF",  # 应该是元器件说明书
        "67 C2988907_2.2KΩ±0.5%100MW_2022-07-08.PDF",  # 应该是元器件说明书
        "70 C2989011_12KΩ±0.5%100MW_2022-07-08.PDF",  # 应该是元器件说明书
        "102 C1669859_32.768KHZ±20PPM7PF_2021-11-26.PDF",  # 应该是元器件说明书
        "1125369445.pdf",  # 应该是芯片数据手册
        "223120313211441084.inform.en.pdf",  # 应该是其他
        "223120315313547084.inform.en.pdf",  # 应该是其他
        "A Blockchain-based Carbon Credit Ecosystem.pdf",  # 应该是其他
        "All-SiC 9.5 kWdm3 On-Board Power Electronics for 50 kW-85 kHz Automotive IPT System.pdf",  # 应该是论文
        "AN-LAN86xx-BIN-Ref-Design-60001718.pdf",  # 应该是技术文档
        "applsci-11-07569-v2.pdf",  # 应该是论文
        "atecc608a_summary.pdf",  # 应该是芯片数据手册
        "atmel-128.pdf",  # 应该是芯片数据手册
        "ChargingPile.pdf",  # 应该是电路图
        "CK45-E3DD472ZYGNA.pdf",  # 应该是元器件说明书
        "Comparison of 22 kHz and 85 kHz 50 kW Wireless Charging System Using Si and SiC Switches for Electric Vehicle.pdf",  # 应该是论文
        "Comprehensive Evaluation of Rectangular and Double-D Coil Geometry for 50 kW-85 kHz IPT System.pdf",  # 应该是论文
        "Control Method for Inductive Power Transfer with High Partial-Load Efficiency and Resonance Tracking.pdf",  # 应该是论文
        "D3V3XA4B10LP.pdf",  # 应该是芯片数据手册
        "datasheet.pdf",  # 应该是芯片数据手册
        "DGD05463.pdf",  # 应该是芯片数据手册
        "DiPho_AFE.pdf",  # 应该是电路图
        "DiPho_digital.pdf",  # 应该是电路图
        "Downloader_C340.pdf",  # 应该是电路图
        "Downloader_cp2104&ch9012f.pdf",  # 应该是电路图
        "EA_TechBrief-10SPE-DT_final.pdf",  # 应该是其他
        "ENIP.cpp Documentation.pdf",  # 应该是技术文档
        "ESP-R8_POE_3_SCHEMATIC.pdf",  # 应该是电路图
        "esp-r8-poe-3.pdf",  # 应该是说明书
        "ESP32_Datasheet.pdf",  # 应该是芯片数据手册
        "ESP32_Hardware_design_guidelines.pdf",  # 应该是技术文档
        "ESP32_picoc_C_Language_Interpreter.pdf",  # 应该是说明书
        "ESP32_Technical_reference_manual.pdf",  # 应该是技术文档
        "esp32_v0a.pdf",  # 应该是电路图
        "esp32_v0b.pdf",  # 应该是电路图
        "ESP32-C6-EVB_Rev_A.pdf",  # 应该是电路图
        "ESP32-EVB_Rev_A.pdf",  # 应该是电路图
        "ESP32-EVB_Rev_B.pdf",  # 应该是电路图
        "ESP32-EVB_Rev_D.pdf",  # 应该是电路图
        "ESP32-EVB_Rev_F.pdf",  # 应该是电路图
        "ESP32-EVB_Rev_H-BOM.pdf",  # 应该是其他
        "ESP32-EVB_Rev_H.pdf",  # 应该是电路图
        "ESP32-EVB_Rev_I-BOM.pdf",  # 应该是其他
        "ESP32-S3 Parallel TFT with Touch 4.0\" ST7701 v1.2.PDF"  # 应该是电路图
    ]
    
    # 期望的分类结果
    expected_results = {
        # 原有期望结果
        "ESP32-DevKit-Lipo_Rev_A1.pdf": "电路图",
        "34 C191602_2.2MH@1KHZ3A_2018-05-02.PDF": "规格书",
        "1N4148WS_Diotec_Semiconductor.pdf": "规格书",
        "WizFi360io_H_SCH_V100.pdf": "电路图",
        "充电桩的采集与监控系统和充电桩.pdf": "专利",
        "充电模块升级技术要求及调研需求2022-5-15.pdf": "技术文档",
        "单相电表模块ATT7053AU使用说明书1.1.pdf": "说明书",
        "永联科技回复.pdf": "其他",
        "海汇德160KW电气原理图纸V1.03.pdf": "图纸",
        "红外读头.pdf": "说明书",
        "苏创自研控制器项目计划.pdf": "技术文档",
        "附件2：应聘登记表.pdf": "其他",
        
        # 新增期望结果
        "1_固德威并网MTG2SMTSDTG2MSDNSXS系列逆变器Modbus通信协议-客户版.pdf": "设备通讯协议",
        "1_固德威并网MTG2SMTSDTG2MSDNSXS系列逆变器Modbus通信协议（正泰是smt）.pdf": "设备通讯协议",
        "1-2 Blue Pill STM32 con LDmicro.pdf": "说明书",
        "4 C2922458_等级_X1,Y24.7NF±10%250VAC_2022-07-26.PDF": "元器件说明书",
        "4-台区智能融合终端功能模块型式规范-征求意见稿.pdf": "企业标准",
        "6.2《大规模电动汽车安全充放电与车-网智能互动关键技术》科学技术项目合同.pdf": "合同",
        "6.78 MHz Wireless Power Transfer with Self Resonant Coils at 95 percent DC-DC Efficiency.pdf": "论文",
        "7-功率分析仪.pdf": "技术文档",
        "08-29-19 PCCC Documentation.pdf": "技术文档",
        "8.1 科学技术项目合同（2023版）-20231117V2.pdf": "合同",
        "8BG000-A7680C-TE_V3.01_DL(230831).pdf": "图纸",
        "11-2.高比例可再生能源接入下考虑运行灵活性的电力系统规划研究-论文1-国网滨州供电公司.pdf": "论文",
        "49 C423021_6.8KΩ±0.5%100MW_2020-03-06.PDF": "元器件说明书",
        "55 C2989257_20KΩ±0.5%100MW_2022-07-08.PDF": "元器件说明书",
        "63 C23186_5.1KΩ±1%100MW_2020-03-06.PDF": "元器件说明书",
        "64 C23162_4.7KΩ±1%100MW_2020-03-06.PDF": "元器件说明书",
        "67 C2988907_2.2KΩ±0.5%100MW_2022-07-08.PDF": "元器件说明书",
        "70 C2989011_12KΩ±0.5%100MW_2022-07-08.PDF": "元器件说明书",
        "102 C1669859_32.768KHZ±20PPM7PF_2021-11-26.PDF": "元器件说明书",
        "1125369445.pdf": "芯片数据手册",
        "223120313211441084.inform.en.pdf": "其他",
        "223120315313547084.inform.en.pdf": "其他",
        "A Blockchain-based Carbon Credit Ecosystem.pdf": "其他",
        "All-SiC 9.5 kWdm3 On-Board Power Electronics for 50 kW-85 kHz Automotive IPT System.pdf": "论文",
        "AN-LAN86xx-BIN-Ref-Design-60001718.pdf": "技术文档",
        "applsci-11-07569-v2.pdf": "论文",
        "atecc608a_summary.pdf": "芯片数据手册",
        "atmel-128.pdf": "芯片数据手册",
        "ChargingPile.pdf": "电路图",
        "CK45-E3DD472ZYGNA.pdf": "元器件说明书",
        "Comparison of 22 kHz and 85 kHz 50 kW Wireless Charging System Using Si and SiC Switches for Electric Vehicle.pdf": "论文",
        "Comprehensive Evaluation of Rectangular and Double-D Coil Geometry for 50 kW-85 kHz IPT System.pdf": "论文",
        "Control Method for Inductive Power Transfer with High Partial-Load Efficiency and Resonance Tracking.pdf": "论文",
        "D3V3XA4B10LP.pdf": "芯片数据手册",
        "datasheet.pdf": "芯片数据手册",
        "DGD05463.pdf": "芯片数据手册",
        "DiPho_AFE.pdf": "电路图",
        "DiPho_digital.pdf": "电路图",
        "Downloader_C340.pdf": "电路图",
        "Downloader_cp2104&ch9012f.pdf": "电路图",
        "EA_TechBrief-10SPE-DT_final.pdf": "其他",
        "ENIP.cpp Documentation.pdf": "技术文档",
        "ESP-R8_POE_3_SCHEMATIC.pdf": "电路图",
        "esp-r8-poe-3.pdf": "说明书",
        "ESP32_Datasheet.pdf": "芯片数据手册",
        "ESP32_Hardware_design_guidelines.pdf": "技术文档",
        "ESP32_picoc_C_Language_Interpreter.pdf": "说明书",
        "ESP32_Technical_reference_manual.pdf": "技术文档",
        "esp32_v0a.pdf": "电路图",
        "esp32_v0b.pdf": "电路图",
        "ESP32-C6-EVB_Rev_A.pdf": "电路图",
        "ESP32-EVB_Rev_A.pdf": "电路图",
        "ESP32-EVB_Rev_B.pdf": "电路图",
        "ESP32-EVB_Rev_D.pdf": "电路图",
        "ESP32-EVB_Rev_F.pdf": "电路图",
        "ESP32-EVB_Rev_H-BOM.pdf": "其他",
        "ESP32-EVB_Rev_H.pdf": "电路图",
        "ESP32-EVB_Rev_I-BOM.pdf": "其他",
        "ESP32-S3 Parallel TFT with Touch 4.0\" ST7701 v1.2.PDF": "电路图"
    }
    
    print("🧪 开始测试分类器准确性...")
    print("=" * 60)
    
    correct_count = 0
    total_count = 0
    
    for filename in test_files:
        # 在标准分类目录中查找文件
        file_found = False
        for category in CATEGORIES:
            test_path = os.path.join("./标准分类", category, filename)
            if os.path.exists(test_path):
                file_found = True
                result = classify_pdf(test_path)
                if result:
                    predicted_category, confidence = result
                    expected_category = expected_results.get(filename, "未知")
                    
                    is_correct = predicted_category == expected_category
                    if is_correct:
                        correct_count += 1
                        status = "✅"
                    else:
                        status = "❌"
                    
                    total_count += 1
                    print(f"{status} {filename}")
                    print(f"   预测: {predicted_category} (置信度: {confidence:.2f})")
                    print(f"   期望: {expected_category}")
                    print()
                break
        
        if not file_found:
            print(f"⚠️  未找到文件: {filename}")
            print()
    
    # 计算准确率
    if total_count > 0:
        accuracy = correct_count / total_count * 100
        print("=" * 60)
        print(f"📊 测试结果:")
        print(f"正确分类: {correct_count}/{total_count}")
        print(f"准确率: {accuracy:.1f}%")
    else:
        print("❌ 没有找到任何测试文件")

def test_category_keywords():
    """测试分类关键词"""
    print("\n🔍 分类关键词测试:")
    print("=" * 60)
    
    for category, config in CATEGORIES.items():
        print(f"\n📁 {category}:")
        print(f"   关键词: {config['keywords']}")
        if 'patterns' in config:
            print(f"   正则表达式: {config['patterns']}")
        print(f"   优先级: {config['priority']}")
        print(f"   最小置信度: {config['min_confidence']}")

if __name__ == "__main__":
    test_specific_files()
    test_category_keywords() 