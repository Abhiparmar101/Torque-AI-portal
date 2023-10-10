from run import app

# Use the app context to access the current user's ID
with app.app_context():
    from run import get_current_user_id

    # Call the function to get the current user's ID
    user_id = get_current_user_id()

    if user_id is not None:
        print(f'Current user ID: {user_id}')
    else:
        print('User is not logged in.')