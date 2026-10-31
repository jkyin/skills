import UIKit

final class PlayerCoverView: UIView {
    private let coverImageView = UIImageView()

    func playbackDidStart() {
        coverImageView.isHidden = true
    }

    func playbackDidEnd() {
        coverImageView.isHidden = false
        bringSubviewToFront(coverImageView)
    }
}
