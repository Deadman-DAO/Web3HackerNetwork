import users.*  // import everything from the users package except given
import users.given // import all given from the users package
import users.User  // import the class User
import users.{User, UserPreferences}  // Only imports selected members
import users.UserPreferences as UPrefs  // import and rename for convenience
import A.{min as minimum, `*` as multiply}
import Predef.{augmentString as _, *}     // imports everything except augmentString
import scala.annotation as ann
import java as j
