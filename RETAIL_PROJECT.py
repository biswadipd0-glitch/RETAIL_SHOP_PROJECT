python
import streamlit as st
import mysql.connector
import QR_CODE_SCANNER


# ============================================================
# MYSQL CLOUD DATABASE CONNECTION
# ============================================================

def get_connection():

    return mysql.connector.connect(

        host=st.secrets["MYSQL_HOST"],

        port=int(
            st.secrets["MYSQL_PORT"]
        ),

        user=st.secrets["MYSQL_USER"],

        password=st.secrets["MYSQL_PASSWORD"],

        database=st.secrets["MYSQL_DATABASE"]
    )


# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="QR Billing System",
    page_icon="🧾",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "customer" not in st.session_state:
    st.session_state.customer = None

if "billing_started" not in st.session_state:
    st.session_state.billing_started = False

if "bill_items" not in st.session_state:
    st.session_state.bill_items = []

if "total_bill_amount" not in st.session_state:
    st.session_state.total_bill_amount = 0.0

if "billing_finished" not in st.session_state:
    st.session_state.billing_finished = False

if "show_registration" not in st.session_state:
    st.session_state.show_registration = False

if "scanned_product" not in st.session_state:
    st.session_state.scanned_product = None


# ============================================================
# CUSTOMER RETRIEVE
# ============================================================

def data_retrieve(ph_no):

    conn_obj = None
    cur_obj = None

    try:

        conn_obj = get_connection()
        cur_obj = conn_obj.cursor()

        sql = """
            SELECT *
            FROM CUST_DETAILS
            WHERE PH_NUMBER = %s
        """

        cur_obj.execute(sql, (ph_no,))

        result = cur_obj.fetchone()

        return result

    except mysql.connector.Error as e:

        st.error(f"Error retrieving customer data: {e}")
        return None

    finally:

        if cur_obj:
            cur_obj.close()

        if conn_obj:
            conn_obj.close()


# ============================================================
# PRODUCT RETRIEVE
# ============================================================

def data_retrieve_from_PRODUCT_DETAILS(p_id):

    conn_obj = None
    cur_obj = None

    try:

        conn_obj = get_connection()
        cur_obj = conn_obj.cursor()

        sql = """
            SELECT *
            FROM PRODUCT_DETAILS
            WHERE P_ID = %s
        """

        cur_obj.execute(sql, (p_id,))

        result = cur_obj.fetchone()

        return result

    except mysql.connector.Error as e:

        st.error(f"Error retrieving product data: {e}")
        return None

    finally:

        if cur_obj:
            cur_obj.close()

        if conn_obj:
            conn_obj.close()


# ============================================================
# GET LAST BILL ID
# ============================================================

def data_retrieve_from_BILL_SUMMARY_TABLE():

    conn_obj = None
    cur_obj = None

    try:

        conn_obj = get_connection()
        cur_obj = conn_obj.cursor()

        sql = """
            SELECT COALESCE(MAX(BILL_ID), 0)
            FROM BILL_SUMMARY_TABLE
        """

        cur_obj.execute(sql)

        result = cur_obj.fetchone()

        return result

    except mysql.connector.Error as e:

        st.error(f"Error retrieving bill ID: {e}")
        return (0,)

    finally:

        if cur_obj:
            cur_obj.close()

        if conn_obj:
            conn_obj.close()


# ============================================================
# INSERT CUSTOMER
# ============================================================

def data_entry_CUST_DETAILS(
    full_name,
    address,
    ph_no_cust
):

    conn_obj = None
    cur_obj = None

    try:

        conn_obj = get_connection()
        cur_obj = conn_obj.cursor()

        sql = """
            INSERT INTO CUST_DETAILS
            (FULL_NAME, ADDRESS, PH_NUMBER)
            VALUES (%s, %s, %s)
        """

        data = (
            full_name,
            address,
            ph_no_cust
        )

        cur_obj.execute(sql, data)

        conn_obj.commit()

        return True

    except mysql.connector.Error as e:

        if conn_obj:
            conn_obj.rollback()

        st.error(
            f"Error inserting customer: {e}"
        )

        return False

    finally:

        if cur_obj:
            cur_obj.close()

        if conn_obj:
            conn_obj.close()


# ============================================================
# INSERT BILL SUMMARY
# ============================================================

def data_entry_BILL_SUMMARY_TABLE(
    bill_id,
    c_id,
    c_name,
    total_bill_value
):

    conn_obj = None
    cur_obj = None

    try:

        conn_obj = get_connection()
        cur_obj = conn_obj.cursor()

        sql = """
            INSERT INTO BILL_SUMMARY_TABLE
            (BILL_ID, C_ID, C_NAME, TOTAL_BILL_VALUE)
            VALUES (%s, %s, %s, %s)
        """

        data = (
            bill_id,
            c_id,
            c_name,
            total_bill_value
        )

        cur_obj.execute(sql, data)

        conn_obj.commit()

        return True

    except mysql.connector.Error as e:

        if conn_obj:
            conn_obj.rollback()

        st.error(
            f"Error inserting bill summary: {e}"
        )

        return False

    finally:

        if cur_obj:
            cur_obj.close()

        if conn_obj:
            conn_obj.close()


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

    conn_obj = None
    cur_obj = None

    try:

        conn_obj = get_connection()
        cur_obj = conn_obj.cursor()

        sql = """
            INSERT INTO BILL_DETAILS_TB
            (BILL_ID, C_ID, P_ID, P_NAME, QUANTITY)
            VALUES (%s, %s, %s, %s, %s)
        """

        data = (
            bill_id,
            c_id,
            p_id,
            p_name,
            quantity
        )

        cur_obj.execute(sql, data)

        conn_obj.commit()

        return True

    except mysql.connector.Error as e:

        if conn_obj:
            conn_obj.rollback()

        st.error(
            f"Error inserting bill details: {e}"
        )

        return False

    finally:

        if cur_obj:
            cur_obj.close()

        if conn_obj:
            conn_obj.close()


# ============================================================
# APPLICATION HEADER
# ============================================================

st.title("🧾 QR CODE BILLING SYSTEM")

st.divider()


# ============================================================
# CUSTOMER SECTION
# ============================================================

st.subheader("👤 Customer Information")


if st.session_state.customer is None:

    phone_number = st.text_input(
        "Enter customer's phone number"
    )

    if st.button(
        "Search Customer",
        type="primary"
    ):

        if not phone_number.strip():

            st.warning(
                "Please enter customer's phone number."
            )

        else:

            cust_details = data_retrieve(
                phone_number.strip()
            )

            if cust_details:

                st.session_state.customer = {
                    "c_id": cust_details[0],
                    "name": cust_details[1],
                    "address": cust_details[2],
                    "phone": cust_details[3]
                }

                st.success(
                    "Existing customer found."
                )

                st.rerun()

            else:

                st.warning(
                    "NEW CUSTOMER. PLEASE REGISTER CUSTOMER DETAILS."
                )

                st.session_state.show_registration = True


# ============================================================
# NEW CUSTOMER REGISTRATION
# ============================================================

if (
    st.session_state.customer is None
    and st.session_state.show_registration
):

    st.subheader("📝 New Customer Registration")

    full_name = st.text_input(
        "Enter Full Name"
    )

    address = st.text_area(
        "Enter Address"
    )

    phone = st.session_state.get(
        "phone_number",
        ""
    )

    st.text_input(
        "Phone Number",
        value=phone,
        disabled=True
    )

    if st.button(
        "Register Customer",
        type="primary"
    ):

        if (
            not full_name.strip()
            or not address.strip()
        ):

            st.warning(
                "Please enter all customer details."
            )

        else:

            success = data_entry_CUST_DETAILS(
                full_name.strip().upper(),
                address.strip().upper(),
                phone.strip()
            )

            if success:

                st.success(
                    "NEW CUSTOMER REGISTRATION SUCCESSFUL."
                )

                cust_details = data_retrieve(
                    phone.strip()
                )

                if cust_details:

                    st.session_state.customer = {
                        "c_id": cust_details[0],
                        "name": cust_details[1],
                        "address": cust_details[2],
                        "phone": cust_details[3]
                    }

                    st.session_state.show_registration = False

                    st.rerun()


# ============================================================
# DISPLAY CUSTOMER
# ============================================================

if st.session_state.customer:

    customer = st.session_state.customer

    st.success("Customer details loaded.")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write("**Customer ID**")
        st.write(customer["c_id"])

    with col2:

        st.write("**Customer Name**")
        st.write(customer["name"])

    with col3:

        st.write("**Phone Number**")
        st.write(customer["phone"])

    st.divider()


# ============================================================
# BILLING
# ============================================================

if st.session_state.customer:

    st.subheader("🛒 Billing")


    # ========================================================
    # START BILLING
    # ========================================================

    if not st.session_state.billing_started:

        if st.button(
            "🚀 START BILLING",
            type="primary"
        ):

            st.session_state.billing_started = True

            st.session_state.billing_finished = False

            st.rerun()


    # ========================================================
    # BILLING STARTED
    # ========================================================

    if st.session_state.billing_started:

        st.info(
            "Click the button below to open the camera "
            "and scan the product QR code."
        )


        # ====================================================
        # SCAN PRODUCT QR
        # ====================================================

        if st.button(
            "📷 SCAN PRODUCT QR",
            type="primary"
        ):

            try:

                # --------------------------------------------
                # THIS OPENS YOUR SEPARATE CAMERA WINDOW
                # --------------------------------------------

                p_id = QR_CODE_SCANNER.qr_code_scanner()


                # --------------------------------------------
                # QR CANCELLED
                # --------------------------------------------

                if p_id is None:

                    st.warning(
                        "QR scanning cancelled."
                    )


                else:

                    st.success(
                        f"QR Code Scanned: {p_id}"
                    )


                    # ----------------------------------------
                    # CONVERT QR VALUE TO INTEGER
                    # ----------------------------------------

                    try:

                        p_id = int(p_id)

                    except ValueError:

                        st.error(
                            "Invalid Product ID in QR code."
                        )

                        st.stop()


                    # ----------------------------------------
                    # GET PRODUCT FROM MYSQL
                    # ----------------------------------------

                    p_details = (
                        data_retrieve_from_PRODUCT_DETAILS(
                            p_id
                        )
                    )


                    if p_details is None:

                        st.error(
                            f"Product ID {p_id} "
                            "does not exist."
                        )


                    else:

                        st.session_state.scanned_product = {
                            "p_id": p_details[0],
                            "p_name": p_details[1],
                            "price": float(p_details[2])
                        }

                        st.rerun()


            except Exception as e:

                st.error(
                    f"Camera error: {e}"
                )


        # ====================================================
        # DISPLAY SCANNED PRODUCT
        # ====================================================

        if st.session_state.scanned_product:

            product = st.session_state.scanned_product

            st.divider()

            st.subheader("📦 Scanned Product")

            col1, col2, col3 = st.columns(3)

            with col1:

                st.write("**Product ID**")
                st.write(product["p_id"])

            with col2:

                st.write("**Product Name**")
                st.write(product["p_name"])

            with col3:

                st.write("**Price**")
                st.write(
                    f"₹ {product['price']:.2f}"
                )


            # =================================================
            # QUANTITY
            # =================================================

            quantity = st.number_input(
                "Enter Quantity",
                min_value=1,
                value=1,
                step=1
            )


            # =================================================
            # ADD PRODUCT
            # =================================================

            if st.button(
                "➕ ADD PRODUCT TO BILL",
                type="primary"
            ):

                last_bill = (
                    data_retrieve_from_BILL_SUMMARY_TABLE()
                )

                last_bill_id = int(
                    last_bill[0]
                )

                new_bill_id = last_bill_id + 1

                amount = (
                    product["price"]
                    * quantity
                )


                success = data_entry_BILL_DETAILS_TB(
                    new_bill_id,
                    st.session_state.customer["c_id"],
                    product["p_id"],
                    product["p_name"],
                    quantity
                )


                if success:

                    st.session_state.bill_items.append({

                        "bill_id": new_bill_id,

                        "p_id": product["p_id"],

                        "p_name": product["p_name"],

                        "price": product["price"],

                        "quantity": quantity,

                        "amount": amount
                    })


                    st.session_state.total_bill_amount += amount


                    # Clear scanned product

                    st.session_state.scanned_product = None


                    st.success(
                        f"{product['p_name']} "
                        "added successfully."
                    )

                    st.rerun()


        # ====================================================
        # CURRENT BILL
        # ====================================================

        if st.session_state.bill_items:

            st.divider()

            st.subheader("🧾 CURRENT BILL")


            for index, item in enumerate(
                st.session_state.bill_items,
                start=1
            ):

                col1, col2, col3, col4, col5 = st.columns(5)


                with col1:

                    st.write(
                        f"**{index}**"
                    )


                with col2:

                    st.write(
                        item["p_name"]
                    )


                with col3:

                    st.write(
                        f"₹ {item['price']:.2f}"
                    )


                with col4:

                    st.write(
                        f"Qty: {item['quantity']}"
                    )


                with col5:

                    st.write(
                        f"₹ {item['amount']:.2f}"
                    )


            st.divider()


            # =================================================
            # TOTAL
            # =================================================

            st.subheader(
                f"💰 TOTAL BILL: "
                f"₹ {st.session_state.total_bill_amount:.2f}"
            )


            # =================================================
            # FINISH BILLING
            # =================================================

            if st.button(
                "✅ FINISH BILLING",
                type="primary"
            ):

                last_bill = (
                    data_retrieve_from_BILL_SUMMARY_TABLE()
                )

                bill_id = (
                    int(last_bill[0]) + 1
                )


                customer = (
                    st.session_state.customer
                )


                success = (
                    data_entry_BILL_SUMMARY_TABLE(

                        bill_id,

                        customer["c_id"],

                        customer["name"],

                        st.session_state.total_bill_amount
                    )
                )


                if success:

                    st.session_state.billing_finished = True

                    st.session_state.billing_started = False

                    st.success(
                        "🎉 BILL COMPLETED SUCCESSFULLY!"
                    )

                    st.rerun()


# ============================================================
# BILL COMPLETED
# ============================================================

if st.session_state.billing_finished:

    st.divider()

    st.success(
        "🎉 BILLING COMPLETED"
    )

    st.subheader(
        f"Final Amount: "
        f"₹ {st.session_state.total_bill_amount:.2f}"
    )


    # ========================================================
    # NEW BILL
    # ========================================================

    if st.button(
        "🆕 START NEW BILL"
    ):

        st.session_state.customer = None

        st.session_state.billing_started = False

        st.session_state.bill_items = []

        st.session_state.total_bill_amount = 0.0

        st.session_state.billing_finished = False

        st.session_state.show_registration = False

        st.session_state.scanned_product = None

        st.rerun()
