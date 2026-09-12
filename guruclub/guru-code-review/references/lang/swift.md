# Swift / iOS 证据检查

检测到相关改动后按需读取。清单提供候选路径，不自动认定缺陷或严重度；以实际 Swift/SDK 版本、项目隔离设置和调用链为准。

## 生命周期与所有权

- 报循环引用前画出实际强持有链，检查完成、取消、失效或显式清理是否能打断。非逃逸或有界回调通常不需要一律加 weak；也不能仅凭 API 名称断言系统回调永远不存在延长生命周期的问题。
- Task 强捕获对象时，检查任务何时结束、等待是否有界以及取消由谁触发。对象不保存 Task handle 也可能被长任务持续持有；保存 handle 本身也不证明永久泄漏。区分循环引用、预期持有与超出页面生命周期的工作。
- unowned、delegate、Timer、CADisplayLink、observer、AnyCancellable 等检查实际所有权和释放路径，不因缺 weak、invalidate 或某个特定存储写法直接报错。unowned 的缺陷须指出对象释放后仍可到达的访问。
- 强解包先验证非 nil 不变量、初始化/回调时序及输入契约。测试中的强解包通常是失败表达方式，但仍可检查它是否阻止必要清理或掩盖真正断言；不机械要求改成 if let。

## 并发与取消

- 先确认 Swift 语言模式、strict concurrency/default actor isolation 配置和 SDK 声明，追踪实际隔离与数据流。缺少显式 MainActor 或 Sendable 标注不单独证明线程错误或数据竞争。
- 区分结构化子任务与 Task / Task.detached 创建的非结构化任务；不要假定替换成 Task 就自动获得父任务取消传播。取消是协作式的，检查被调用 API 是否响应取消及调用方是否需要停止后续副作用。[Swift SE-0304](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0304-structured-concurrency.md)
- Task.detached 的上下文继承与结构化任务不同；只有缺失的隔离/优先级/任务局部信息造成具体问题时才报告，不能以“没有理由”替代证据。
- actor 在 await 处可能让出执行，核实恢复后依赖的不变量是否仍成立，以及是否有重新验证、版本号或其他同步保护。
- 页面消失、cell 复用或请求替换后，沿启动、取消、完成和晚到回调检查状态。未显式检查 Task.isCancelled 不一定是缺陷，若底层已抛取消或工作允许继续则应排除。

## UI、数据与兼容性

- UIKit 更新、状态发布：核实要求的执行上下文和真实调用队列，不能把所有网络回调都当作后台执行。
- cell 复用/异步图片：检查绑定新数据、取消旧请求、身份校验和晚到回调；prepareForReuse 没某行代码不等于必然串位。
- SwiftUI 所有权和 identity：对象在哪里创建、谁应持有、视图身份何时改变、列表 ID 是否在实际更新中保持稳定。不要仅凭 StateObject/ObservedObject、下标或 self 字面用法作结论。
- 错误处理、Codable/null、桥接 IUO、selector：结合服务契约、fallback、调用方和具体输入证明错误路径，不把 try? 或空 catch 自动认定为 bug。
- API 可用性：核对真实 deployment target、SDK 声明与 guard/fallback；不要按印象或最新系统版本判断。
- final、访问控制、框架选择等只有影响公共契约、运行行为或违反当前有效项目规则时才报告。另一客户端的专属规则不能自动成为本客户端约束。

## 输出依据

每条候选说明本轮哪处变更、何种可达条件、实际影响以及为何现有处理不足。需要特定 SDK 行为才能成立时查当前官方资料或做范围内复现；证据不全就说明边界，不填高置信度。

优先比较真正可比的同模块实现和消费者；严重度由触发概率、影响范围及可恢复性决定，不给某类语法或持有链固定 CRITICAL。
