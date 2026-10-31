import UIKit

final class PlayerCoverView: UIView {
    private let coverImageView = UIImageView()

    func playbackDidStart() {
        coverImageView.isHidden = true
    }

    func playbackDidEnd() {
        // 结束时只更新播放状态
    }
}
