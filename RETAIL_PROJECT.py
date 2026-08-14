import streamlit as st
import mysql.connector
import numpy as np

from PIL import Image

from camera_input_live import camera_input_live

from qr_code_scanner import qr_code_scanner


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Retail Shop Billing System",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 Retail Shop Billing System")


# ============================================================
# MYSQL CLOUD CONNECTION
# ============================================================

def get_connection():

    return mysql.connector.connect(
        host=st.secrets["MYSQL_HOST"],
        port=int(st.secrets["MYSQL_PORT"]),
        user=st.secrets["MYSQL_USER"],
        password=st.secrets["MYSQL_PASSWORD"],
        database=st.secrets["MYSQL_DATABASE"]
    )


# ============================================================
# INSERT CUSTOMER DETAILS
# ============================================================

def data_entry_CUST_DETAILS(
    full_name,
    address,
    ph_no_cust
):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO CUST_DETAILS
            (
                FULL_NAME,
                ADDRESS,
                PH_NUMBER
            )
            VALUES (%s, %s, %s)
        """

        data = (
            full_name,
            address,
            ph_no_cust
        )

        cursor.execute(
            sql,
            data
        )

        conn.commit()

        return (
            True,
            "NEW CUSTOMER REGISTRATION SUCCESSFUL."
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        return (
            False,
            f"Error inserting customer: {e}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# INSERT BILL SUMMARY
# ============================================================

def data_entry_BILL_SUMMARY_TABLE(
    c_id,
    c_name,
    total_bill_value
):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO BILL_SUMMARY_TABLE
            (
                C_ID,
                C_NAME,
                TOTAL_BILL_VALUE
            )
            VALUES (%s, %s, %s)
        """

        data = (
            c_id,
            c_name,
            total_bill_value
        )

        cursor.execute(
            sql,
            data
        )

        conn.commit()

        # BILL_ID should be AUTO_INCREMENT
        bill_id = cursor.lastrowid

        return (
            True,
            bill_id
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        return (
            False,
            f"Error inserting bill summary: {e}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# INSERT BILL DETAILS
# ============================================================

def data_entry_BILL_DETAILS_TB(
    bill_id,
    c_id,
    p_id,
    p_name,
    quantity
):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO BILL_DETAILS_TB
            (
                BILL_ID,
                C_ID,
                P_ID,
                P_NAME,
                QUANTITY
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        data = (
            bill_id,
            c_id,
            p_id,
            p_name,
            quantity
        )

        cursor.execute(
            sql,
            data
        )

        conn.commit()

        return (
            True,
            "Bill details inserted successfully."
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        return (
            False,
            f"Error inserting bill details: {e}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# UPDATE BILL TOTAL
# ============================================================

def update_bill_total(
    bill_id,
    total_amount
):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            UPDATE BILL_SUMMARY_TABLE
            SET TOTAL_BILL_VALUE = %s
            WHERE BILL_ID = %s
        """

        cursor.execute(
            sql,
            (
                total_amount,
                bill_id
            )
        )

        conn.commit()

        return True

    except mysql.connector.Error:

        if conn:
            conn.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# RETRIEVE CUSTOMER
# ============================================================

def data_retrieve(ph_no):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT *
            FROM CUST_DETAILS
            WHERE PH_NUMBER = %s
        """

        cursor.execute(
            sql,
            (ph_no,)
        )

        result = cursor.fetchone()

        return result

    except mysql.connector.Error as e:

        st.error(
            f"Error retrieving customer: {e}"
        )

        return None

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# RETRIEVE PRODUCT
# ============================================================

def data_retrieve_from_PRODUCT_DETAILS(
    p_id
):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT *
            FROM PRODUCT_DETAILS
            WHERE P_ID = %s
        """

        cursor.execute(
            sql,
            (p_id,)
        )

        result = cursor.fetchone()

        return result

    except mysql.connector.Error as e:

        st.error(
            f"Error retrieving product: {e}"
        )

        return None

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# SESSION STATE
# ============================================================

if "customer" not in st.session_state:

    st.session_state.customer = None


if "phone_number" not in st.session_state:

    st.session_state.phone_number = ""


if "billing_started" not in st.session_state:

    st.session_state.billing_started = False


if "bill_id" not in st.session_state:

    st.session_state.bill_id = None


if "total_bill" not in st.session_state:

    st.session_state.total_bill = 0.0


if "bill_items" not in st.session_state:

    st.session_state.bill_items = []


if "product_details" not in st.session_state:

    st.session_state.product_details = None


if "last_detected_p_id" not in st.session_state:

    st.session_state.last_detected_p_id = None


if "camera_active" not in st.session_state:

    st.session_state.camera_active = False


# ============================================================
# CUSTOMER SECTION
# ============================================================

if not st.session_state.billing_started:

    st.header("👤 Customer Details")


    phone = st.text_input(
        "Enter customer's phone number",
        value=st.session_state.phone_number
    ).strip()


    st.session_state.phone_number = phone


    # ========================================================
    # SEARCH CUSTOMER
    # ========================================================

    if st.button(
        "🔍 Search Customer",
        type="primary"
    ):

        if phone == "":

            st.warning(
                "Please enter customer's phone number."
            )

        else:

            customer = data_retrieve(phone)


            if customer:

                st.session_state.customer = customer

                st.success(
                    "EXISTING CUSTOMER FOUND."
                )

            else:

                st.session_state.customer = "NEW"

                st.info(
                    "NEW CUSTOMER. "
                    "PLEASE REGISTER CUSTOMER DETAILS."
                )


    # ========================================================
    # EXISTING CUSTOMER
    # ========================================================

    if (
        st.session_state.customer is not None
        and
        st.session_state.customer != "NEW"
    ):

        customer = st.session_state.customer


        st.subheader(
            "Existing Customer Details"
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.write(
                f"**Customer ID:** {customer[0]}"
            )


        with col2:

            st.write(
                f"**Customer Name:** {customer[1]}"
            )


        with col3:

            st.write(
                f"**Address:** {customer[2]}"
            )


        # ====================================================
        # START BILLING
        # ====================================================

        if st.button(
            "🛒 Start Billing",
            type="primary"
        ):

            success, result = (
                data_entry_BILL_SUMMARY_TABLE(
                    customer[0],
                    customer[1],
                    0
                )
            )


            if success:

                st.session_state.billing_started = True

                st.session_state.bill_id = result

                st.session_state.total_bill = 0.0

                st.session_state.bill_items = []

                st.session_state.product_details = None

                st.session_state.last_detected_p_id = None

                st.session_state.camera_active = True

                st.rerun()

            else:

                st.error(result)


    # ========================================================
    # NEW CUSTOMER
    # ========================================================

    elif (
        st.session_state.customer == "NEW"
    ):

        st.subheader(
            "🆕 New Customer Registration"
        )


        full_name = st.text_input(
            "Full Name"
        ).strip().upper()


        address = st.text_area(
            "Address"
        ).strip().upper()


        if st.button(
            "📝 Register Customer",
            type="primary"
        ):

            if (
                full_name == ""
                or
                address == ""
            ):

                st.warning(
                    "Please enter full name "
                    "and address."
                )

            else:

                success, message = (
                    data_entry_CUST_DETAILS(
                        full_name,
                        address,
                        phone
                    )
                )


                if success:

                    st.success(message)


                    customer = data_retrieve(
                        phone
                    )


                    if customer:

                        st.session_state.customer = (
                            customer
                        )

                        st.rerun()

                else:

                    st.error(message)


# ============================================================
# BILLING SECTION
# ============================================================

if st.session_state.billing_started:

    customer = st.session_state.customer


    st.divider()

    st.header("🛒 Billing")


    # ========================================================
    # BILL INFORMATION
    # ========================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Customer",
            customer[1]
        )


    with col2:

        st.metric(
            "Bill ID",
            st.session_state.bill_id
        )


    with col3:

        st.metric(
            "Total Amount",
            f"₹ "
            f"{st.session_state.total_bill:.2f}"
        )


    # ========================================================
    # CAMERA SECTION
    # ========================================================

    st.divider()

    st.subheader(
        "📷 QR Code Scanner"
    )


    st.info(
        """
Show the product QR code clearly in front of
the camera.

Example QR content:

101-ABC123

The scanner will extract:

101

and use 101 as the Product ID.
"""
    )


    # ========================================================
    # LIVE CAMERA
    # ========================================================

    camera_image = camera_input_live(
        key="live_qr_camera"
    )


    # ========================================================
    # PROCESS CAMERA IMAGE
    # ========================================================

    if camera_image is not None:

        try:

            # Read image from camera

            image = Image.open(
                camera_image
            ).convert("RGB")


            # Convert PIL image to NumPy
            # array for pyzbar

            frame = np.array(
                image
            )


            # Send frame to your
            # separate QR scanner

            p_id = qr_code_scanner(
                frame
            )


            # =================================================
            # QR DETECTED
            # =================================================

            if p_id is not None:

                # Only process the QR if it is
                # different from the previous QR.

                if (
                    p_id
                    !=
                    st.session_state.last_detected_p_id
                ):

                    st.session_state.last_detected_p_id = (
                        p_id
                    )


                    st.success(
                        "✅ QR Code Scanned Successfully"
                    )


                    st.write(
                        f"**Product ID:** {p_id}"
                    )


                    # -----------------------------------------
                    # Product lookup
                    # -----------------------------------------

                    product = (
                        data_retrieve_from_PRODUCT_DETAILS(
                            p_id
                        )
                    )


                    if product:

                        st.session_state.product_details = (
                            product
                        )


                        # No camera stop here.
                        # Camera remains active.

                    else:

                        st.error(
                            f"Product ID {p_id} "
                            "was not found in "
                            "PRODUCT_DETAILS."
                        )


        except Exception as e:

            st.error(
                f"Camera scanning error: {e}"
            )


    # ========================================================
    # PRODUCT DETAILS
    # ========================================================

    if st.session_state.product_details:

        product = (
            st.session_state.product_details
        )


        st.divider()

        st.subheader(
            "📦 Scanned Product"
        )


        # ----------------------------------------------------
        # PRODUCT INFORMATION
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)


        with col1:

            st.write(
                f"**Product ID:** "
                f"{product[0]}"
            )


        with col2:

            st.write(
                f"**Product Name:** "
                f"{product[1]}"
            )


        with col3:

            st.write(
                f"**Price:** "
                f"₹ {float(product[2]):.2f}"
            )


        # ----------------------------------------------------
        # QUANTITY
        # ----------------------------------------------------

        quantity = st.number_input(

            "Enter Quantity",

            min_value=1,

            value=1,

            step=1,

            key=f"quantity_{product[0]}"
        )


        # ----------------------------------------------------
        # AMOUNT
        # ----------------------------------------------------

        amount = (
            float(product[2])
            *
            quantity
        )


        st.info(
            f"Product Amount: "
            f"₹ {amount:.2f}"
        )


        # ----------------------------------------------------
        # ADD PRODUCT
        # ----------------------------------------------------

        if st.button(
            "➕ Add Product to Bill",
            type="primary"
        ):

            success, message = (
                data_entry_BILL_DETAILS_TB(

                    st.session_state.bill_id,

                    customer[0],

                    product[0],

                    product[1],

                    quantity
                )
            )


            if success:

                # --------------------------------------------
                # Update total
                # --------------------------------------------

                st.session_state.total_bill += (
                    amount
                )


                # --------------------------------------------
                # Update bill summary
                # --------------------------------------------

                update_bill_total(

                    st.session_state.bill_id,

                    st.session_state.total_bill
                )


                # --------------------------------------------
                # Add item to bill
                # --------------------------------------------

                st.session_state.bill_items.append(

                    {
                        "Product ID": product[0],

                        "Product Name": product[1],

                        "Price": float(
                            product[2]
                        ),

                        "Quantity": quantity,

                        "Amount": amount
                    }
                )


                # --------------------------------------------
                # Clear product
                # --------------------------------------------

                st.session_state.product_details = (
                    None
                )


                # --------------------------------------------
                # IMPORTANT
                #
                # We do NOT stop the camera.
                #
                # But we keep the previous ID until
                # the QR is removed from the camera.
                # --------------------------------------------

                st.success(
                    f"{product[1]} "
                    "added successfully."
                )


            else:

                st.error(message)


    # ========================================================
    # CURRENT BILL
    # ========================================================

    st.divider()

    st.subheader(
        "🧾 Current Bill"
    )


    if st.session_state.bill_items:

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        h1, h2, h3, h4, h5 = st.columns(5)


        with h1:

            st.write("**No.**")


        with h2:

            st.write("**Product ID**")


        with h3:

            st.write("**Product Name**")


        with h4:

            st.write("**Quantity / Price**")


        with h5:

            st.write("**Amount**")


        st.divider()


        # ----------------------------------------------------
        # Items
        # ----------------------------------------------------

        for index, item in enumerate(
            st.session_state.bill_items,
            start=1
        ):

            c1, c2, c3, c4, c5 = (
                st.columns(5)
            )


            with c1:

                st.write(
                    index
                )


            with c2:

                st.write(
                    item["Product ID"]
                )


            with c3:

                st.write(
                    item["Product Name"]
                )


            with c4:

                st.write(
                    f'{item["Quantity"]} × '
                    f'₹ {item["Price"]:.2f}'
                )


            with c5:

                st.write(
                    f'₹ {item["Amount"]:.2f}'
                )


        st.divider()


        st.subheader(
            f"💰 Total Bill Amount: "
            f"₹ {st.session_state.total_bill:.2f}"
        )


    else:

        st.info(
            "No products added to the bill yet."
        )


    # ========================================================
    # RESET SCANNER
    # ========================================================

    st.divider()


    if st.button(
        "🔄 Ready for Next QR"
    ):

        st.session_state.last_detected_p_id = (
            None
        )

        st.session_state.product_details = (
            None
        )

        st.rerun()


    # ========================================================
    # FINISH BILLING
    # ========================================================

    st.divider()


    if st.button(
        "✅ Finish Billing",
        type="primary"
    ):

        # ----------------------------------------------------
        # Final total update
        # ----------------------------------------------------

        update_bill_total(

            st.session_state.bill_id,

            st.session_state.total_bill
        )


        # ----------------------------------------------------
        # Store values before clearing
        # ----------------------------------------------------

        completed_bill_id = (
            st.session_state.bill_id
        )

        completed_customer_name = (
            customer[1]
        )

        completed_total = (
            st.session_state.total_bill
        )


        # ----------------------------------------------------
        # Reset
        # ----------------------------------------------------

        st.session_state.billing_started = False

        st.session_state.bill_id = None

        st.session_state.total_bill = 0.0

        st.session_state.bill_items = []

        st.session_state.product_details = None

        st.session_state.last_detected_p_id = None

        st.session_state.customer = None

        st.session_state.camera_active = False


        # ----------------------------------------------------
        # Completion message
        # ----------------------------------------------------

        st.success(
            f"""
✅ BILLING COMPLETED SUCCESSFULLY

Bill ID: {completed_bill_id}

Customer: {completed_customer_name}

Total Amount:
₹ {completed_total:.2f}
"""
        )


        st.rerun()
