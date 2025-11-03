"""简单的 API 测试脚本"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000/api"


async def test_workflow():
    """测试完整的生成流程"""
    async with httpx.AsyncClient() as client:
        print("🧪 开始测试 Novel Studio API...\n")
        
        # 1. 创建工作区
        print("1️⃣ 创建工作区...")
        workspace_resp = await client.post(
            f"{BASE_URL}/workspace",
            json={
                "title": "测试小说",
                "genre": "玄幻",
                "description": "这是一个测试小说",
                "tags": ["测试", "玄幻"]
            }
        )
        workspace_resp.raise_for_status()
        workspace = workspace_resp.json()
        workspace_id = workspace["id"]
        print(f"   ✓ 工作区创建成功，ID: {workspace_id}\n")
        
        # 2. 生成大纲
        print("2️⃣ 生成第1章大纲...")
        plan_resp = await client.post(
            f"{BASE_URL}/plan",
            json={
                "workspace_id": workspace_id,
                "chapter_number": 1,
                "user_input": "主角是一个修仙者，在山中修炼"
            }
        )
        plan_resp.raise_for_status()
        plan_result = plan_resp.json()
        chapter_id = plan_result["chapter_id"]
        print(f"   ✓ 大纲生成成功")
        print(f"   大纲预览: {plan_result['plan'][:200]}...\n")
        
        # 3. 生成内容
        print("3️⃣ 生成章节内容...")
        generate_resp = await client.post(
            f"{BASE_URL}/generate",
            json={
                "chapter_id": chapter_id,
                "regenerate": False
            }
        )
        generate_resp.raise_for_status()
        generate_result = generate_resp.json()
        print(f"   ✓ 内容生成成功")
        print(f"   内容预览: {generate_result['content'][:200]}...\n")
        
        # 4. 验证内容
        print("4️⃣ 验证章节内容...")
        verify_resp = await client.post(
            f"{BASE_URL}/verify",
            json={
                "chapter_id": chapter_id
            }
        )
        verify_resp.raise_for_status()
        verify_result = verify_resp.json()
        print(f"   ✓ 验证完成")
        print(f"   通过: {verify_result['passed']}")
        if verify_result['issues']:
            print(f"   问题: {verify_result['issues']}")
        print()
        
        # 5. 如果未通过，改进内容
        if not verify_result['passed']:
            print("5️⃣ 改进章节内容...")
            improve_resp = await client.post(
                f"{BASE_URL}/improve",
                json={
                    "chapter_id": chapter_id
                }
            )
            improve_resp.raise_for_status()
            improve_result = improve_resp.json()
            print(f"   ✓ 内容改进成功")
            print(f"   改进后内容预览: {improve_result['improved_content'][:200]}...\n")
            
            # 重新验证
            print("   重新验证...")
            verify_resp = await client.post(
                f"{BASE_URL}/verify",
                json={
                    "chapter_id": chapter_id
                }
            )
            verify_resp.raise_for_status()
            verify_result = verify_resp.json()
            print(f"   ✓ 验证完成")
            print(f"   通过: {verify_result['passed']}\n")
        
        # 6. 最终确认
        if verify_result['passed']:
            print("6️⃣ 最终确认章节...")
            finalize_resp = await client.post(
                f"{BASE_URL}/finalize/{chapter_id}"
            )
            finalize_resp.raise_for_status()
            finalize_result = finalize_resp.json()
            print(f"   ✓ 章节已完成\n")
        
        # 7. 查看章节列表
        print("7️⃣ 查看章节列表...")
        chapters_resp = await client.get(
            f"{BASE_URL}/workspace/{workspace_id}/chapters"
        )
        chapters_resp.raise_for_status()
        chapters = chapters_resp.json()
        print(f"   ✓ 共有 {len(chapters)} 个章节")
        for ch in chapters:
            print(f"   - 第{ch['chapter_number']}章: {ch['title'] or '未命名'} [{ch['status']}]")
        print()
        
        print("✅ 所有测试通过！")


async def test_health():
    """测试健康检查"""
    async with httpx.AsyncClient() as client:
        print("🏥 测试健康检查...")
        try:
            resp = await client.get("http://localhost:8000/health")
            resp.raise_for_status()
            print(f"   ✓ 服务健康: {resp.json()}\n")
            return True
        except Exception as e:
            print(f"   ✗ 服务未启动: {e}")
            print("   请先运行: python backend/main.py\n")
            return False


async def main():
    # 先检查服务是否启动
    if not await test_health():
        return
    
    # 运行完整测试
    try:
        await test_workflow()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

