import UIKit

final class FeedEmptyView: UIView {
    let titleLabel = UILabel()

    func configure() {
        titleLabel.text = "暂无内容，下拉刷新是是"
    }
}
