vc_template = """\
import UIKit

class <name>ViewController: UIViewController {
    // MARK: Variables

    // MARK: View Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()

        setView()
        setConstraints()
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    func setView() {
    }

    func setConstraints() {

    }

    // MARK: Interactions

    // MARK: Helpers
}

// MARK: Extensions

// MARK: Constants
extension <name>ViewController {
    enum localConstants {
        enum texts {
        }
        enum assets {
        }
         enum keys {
        }
    }
}
"""
