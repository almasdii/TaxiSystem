from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Callable
from fastapi import status
from fastapi import FastAPI


class UserException(Exception):
	pass
class UserAlreadyExists(UserException):
	pass
class InvalidCredentials(UserException):
	pass
class AccessTokenRequired(Exception):
	pass
class InvalidToken(Exception):
	pass
class RefreshTokenRequired(Exception):
	pass
class UserNotFoundByEmail(UserException):
	pass
class AccessForbidden(UserException):
	pass


class CarException(Exception):
	pass
class PassengerCannotManageCarException(CarException):
		pass
class InactiveOrBannedDriverException(CarException):
		pass
class DuplicatePlateNumberException(CarException):
		pass
class DriverCarOwnershipException(CarException):
		pass
class InvalidCarSeatsException(CarException):
		pass
class CarNotFoundException(CarException):
		pass
class DriverWithoutCarException(UserException):
    pass



class InvalidTripSeatsException(Exception):
    pass
class TripAlreadyStartedException(Exception):
    pass
class InvalidTripRouteException(Exception):
    pass
class DriverTripOwnershipException(Exception):
    pass
class TripAlreadyCompletedException(Exception):
    pass


class TripNotFoundException(Exception):
    pass
class DuplicateRouteOrderException(Exception):
    pass
class InvalidRoutePointTimeException(Exception):
    pass
class RoutePointNotFoundException(Exception):
    pass
class TripAlreadyStartedException(Exception):
    pass
class RoutePointOrderConflictException(Exception):
	pass

class InvalidRoutePointsException(UserException):
    pass


class PickupAfterDropoffException(UserException):
    pass


class NoSeatsAvailableException(Exception):
    pass
class PassengerOwnTripException(Exception):
    pass
class DuplicateBookingException(Exception):
    pass
class BookingOwnershipException(Exception):
    pass
class BookingAlreadyCancelledException(Exception):
    pass

def create_exception_handler(
		status_code:int,
		initial_detail:str
) -> Callable[[Request,Exception],JSONResponse]:
	async def exception_handler(request:Request, exc:Exception) -> JSONResponse:
		return JSONResponse(
			status_code=status_code,
			content={"detail": f"{initial_detail}: {str(exc)}"}
		)
	return exception_handler

def register_error_handlers(app: FastAPI):
		app.add_exception_handler(
				UserAlreadyExists,
				create_exception_handler(
						status_code=status.HTTP_409_CONFLICT,
						initial_detail={
								"message": "User with email already exists",
								"error_code": "user_exists",
						},
				),
			)	
		app.add_exception_handler(
				InvalidCredentials,
				create_exception_handler(
						status_code=status.HTTP_401_UNAUTHORIZED,
						initial_detail={
								"message": "Invalid email or password",
								"error_code": "invalid_credentials",
						},
				),
			)
		app.add_exception_handler(
				AccessTokenRequired,
				create_exception_handler(
						status_code=status.HTTP_401_UNAUTHORIZED,
						initial_detail={
								"message": "Access token is required",
								"error_code": "access_token_required",
						},
				),
		)
		app.add_exception_handler(
				InvalidToken,
				create_exception_handler(
						status_code=status.HTTP_401_UNAUTHORIZED,
						initial_detail={
								"message": "This token is invalid or expired",
								"error_code": "invalid_token",
						},
				),
		)
		app.add_exception_handler(
				RefreshTokenRequired,
				create_exception_handler(
						status_code=status.HTTP_401_UNAUTHORIZED,
						initial_detail={
								"message": "Refresh token is required",
								"error_code": "refresh_token_required",
						},
				),
		)
		app.add_exception_handler(
			UserNotFoundByEmail,
			create_exception_handler(
				status_code=status.HTTP_404_NOT_FOUND,
				initial_detail={
					"message" : "User not found by this email",
					"error_code": "not_found"
				}
			)
		)
		app.add_exception_handler(
			AccessForbidden,
			create_exception_handler(
				status_code=status.HTTP_403_FORBIDDEN,
				initial_detail={
					"message" : "User cannot change account since its not his account",
					"error_code": "forbidden"
				}
			)
		)

		app.add_exception_handler(
		PassengerCannotManageCarException,
		create_exception_handler(
				status_code=status.HTTP_403_FORBIDDEN,
				initial_detail={
						"message": "Passenger cannot manage cars",
						"error_code": "passenger_cannot_manage_car",
						},
				),
		)
		app.add_exception_handler(
		InactiveOrBannedDriverException,
		create_exception_handler(
				status_code=status.HTTP_403_FORBIDDEN,
				initial_detail={
						"message": "Inactive or banned driver cannot manage cars",
						"error_code": "driver_inactive",
						},
				),
		)
				
		app.add_exception_handler(
		DuplicatePlateNumberException,
		create_exception_handler(
				status_code=status.HTTP_409_CONFLICT,
				initial_detail={
						"message": "Car with this plate number already exists",
						"error_code": "duplicate_plate",
						},
				),
		)
				
		app.add_exception_handler(
		DriverCarOwnershipException,
		create_exception_handler(
				status_code=status.HTTP_403_FORBIDDEN,
				initial_detail={
						"message": "You are not the owner of this car",
						"error_code": "car_owner_only",
						},
				),
		)
		app.add_exception_handler(
		InvalidCarSeatsException,
		create_exception_handler(
				status_code=status.HTTP_400_BAD_REQUEST,
				initial_detail={
						"message": "Invalid number of seats",
						"error_code": "invalid_car_seats",
						},
				),
		)
		app.add_exception_handler(
		CarNotFoundException,
		create_exception_handler(
				status_code=status.HTTP_404_NOT_FOUND,
				initial_detail={
						"message": "Car not found",
						"error_code": "car_not_found",
						},
				),
		)

		app.add_exception_handler(
    DriverWithoutCarException,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "Driver must register a car before creating a trip",
            "error_code": "driver_without_car",
						},
				),
		)
		app.add_exception_handler(
    InvalidTripSeatsException,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "Trip seats exceed car capacity",
            "error_code": "invalid_trip_seats",
						},
				),
		)
		app.add_exception_handler(
    TripAlreadyStartedException,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "Trip start time must be in the future",
            "error_code": "trip_already_started",
						},
				),
		)

		app.add_exception_handler(
    InvalidTripRouteException,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "Origin and destination cannot be the same",
            "error_code": "invalid_trip_route",
						},
				),
		)

		app.add_exception_handler(
    TripAlreadyCompletedException,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "Trip is already completed",
            "error_code": "trip_completed",
						},
				),
		)
		app.add_exception_handler(
    DriverTripOwnershipException,
    create_exception_handler(
        status_code=status.HTTP_403_FORBIDDEN,
        initial_detail={
            "message": "You are not the owner of this trip",
            "error_code": "trip_owner_only",
						},
				),
		)

		app.add_exception_handler(
    TripNotFoundException,
    create_exception_handler(
        status_code=status.HTTP_404_NOT_FOUND,
        initial_detail={
            "message": "Trip not found",
            "error_code": "trip_not_found",
						},
				),
		)
		
		app.add_exception_handler(
    DuplicateRouteOrderException,
    create_exception_handler(
        status_code=status.HTTP_409_CONFLICT,
        initial_detail={
            "message": "Route point order already exists in this trip",
            "error_code": "duplicate_route_order",
						},
				),
		)
		
		app.add_exception_handler(
    InvalidRoutePointTimeException,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "Route point time must be before trip start time",
            "error_code": "invalid_route_point_time",
						},
				),
		)
		
		app.add_exception_handler(
    RoutePointNotFoundException,
    create_exception_handler(
        status_code=status.HTTP_404_NOT_FOUND,
        initial_detail={
            "message": "Route point not found",
            "error_code": "route_point_not_found",
						},
				),
		)
		
		app.add_exception_handler(
    TripAlreadyStartedException,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "Trip already started. Route cannot be modified",
            "error_code": "trip_already_started",
						},
				),
		)

		app.add_exception_handler(
    InvalidRoutePointsException,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "Route points must belong to the same trip",
            "error_code": "invalid_route_points",
						},
				),
		)

		app.add_exception_handler(
    PickupAfterDropoffException,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "Pickup route point must come before dropoff route point",
            "error_code": "pickup_after_dropoff",
						},
				),
		)

		app.add_exception_handler(
    PickupAfterDropoffException,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "Pickup route point must come before dropoff route point",
            "error_code": "pickup_after_dropoff",
						},
				),
		)

		app.add_exception_handler(
    NoSeatsAvailableException,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "No seats available for this trip",
            "error_code": "no_seats_available",
						},
				),
		)

		app.add_exception_handler(
    NoSeatsAvailableException,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "No seats available for this trip",
            "error_code": "no_seats_available",
						},
				),
		)

		app.add_exception_handler(
    DuplicateBookingException,
    create_exception_handler(
        status_code=status.HTTP_409_CONFLICT,
        initial_detail={
            "message": "Passenger already booked this trip",
            "error_code": "duplicate_booking",
						},
				),
		)

		app.add_exception_handler(
    BookingOwnershipException,
    create_exception_handler(
        status_code=status.HTTP_403_FORBIDDEN,
        initial_detail={
            "message": "You are not allowed to access this booking",
            "error_code": "booking_ownership",
						},
				),
		)

		app.add_exception_handler(
    BookingAlreadyCancelledException,
    create_exception_handler(
        status_code=status.HTTP_400_BAD_REQUEST,
        initial_detail={
            "message": "Booking is already cancelled",
            "error_code": "booking_cancelled",
						},
				),
		)